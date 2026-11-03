"""Run reproducible local regressions; each report contains one run plus history."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

parser = argparse.ArgumentParser()
parser.add_argument('--runs', type=int, default=3)
parser.add_argument('--allure', default='allure')
parser.add_argument('--selenoid-url')
parser.add_argument('--output', default='regression')
parser.add_argument('--previous', help='Previous Allure report to carry history from')
parser.add_argument('--build-start', type=int, default=1)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
output = root / args.output
output.mkdir(parents=True, exist_ok=True)
source_files = sorted(
    [p for folder in ['app', 'pages', 'tests', 'features', 'data', 'ci', 'selenoid', '.github']
     for p in (root / folder).rglob('*')
     if p.is_file() and '__pycache__' not in p.parts]
    + [root / name for name in ['conftest.py', 'pytest.ini', 'requirements.txt', 'requirements.lock.txt']])
digest = hashlib.sha256()
for file in source_files:
    digest.update(file.relative_to(root).as_posix().encode())
    digest.update(file.read_bytes())
source_hash = digest.hexdigest()
previous = Path(args.previous).resolve() if args.previous else None
records = []


def execute(command, log, env):
    started = time.perf_counter()
    with log.open('w', encoding='utf-8') as stream:
        result = subprocess.run(command, cwd=root, env=env, stdout=stream, stderr=subprocess.STDOUT)
    duration = time.perf_counter() - started
    print(log.name, 'exit', result.returncode, f'{duration:.3f}s', flush=True)
    return {'exit_code': result.returncode, 'wall_seconds': duration, 'log': str(log.relative_to(root))}


for number in range(1, args.runs + 1):
    run = output / f'run-{number}'
    if run.exists():
        raise SystemExit('Refusing to mix existing results: ' + str(run))
    run.mkdir()
    raw = run / 'allure-results'
    env = dict(os.environ, BROWSER='chromium', PYTHONIOENCODING='utf-8')
    record = {'run': number, 'source_sha256': source_hash,
              'started': datetime.now(timezone.utc).isoformat(), 'stages': {}}
    full_started = time.perf_counter()
    command = [sys.executable, '-m', 'pytest', 'tests/unit', 'tests/api', 'tests/ui', '-q',
               '--cov=app', '--cov-branch', '--cov-report=json:' + str(run / 'coverage.json'),
               '--cov-report=html:' + str(run / 'htmlcov'),
               '--junitxml=' + str(run / 'pytest.xml'), '--alluredir=' + str(raw)]
    record['stages']['chromium'] = execute(command, run / 'pytest.log', env)
    env['BROWSER'] = 'firefox'
    command = [sys.executable, '-m', 'pytest', 'tests/ui', '-q',
               '--junitxml=' + str(run / 'firefox.xml'), '--alluredir=' + str(raw)]
    record['stages']['firefox'] = execute(command, run / 'firefox.log', env)
    env['BROWSER'] = 'chromium'
    command = [sys.executable, '-m', 'behave', 'features/select_menu.feature',
               '--junit', '--junit-directory', str(run / 'bdd'),
               '-f', 'allure_behave.formatter:AllureFormatter', '-o', str(raw),
               '-f', 'pretty', '--no-color']
    record['stages']['bdd'] = execute(command, run / 'bdd.log', env)
    if args.selenoid_url:
        env['SELENOID_URL'] = args.selenoid_url
        env['SELENOID_EVIDENCE'] = str(run / 'selenoid')
        command = [sys.executable, '-m', 'pytest', 'tests/selenoid', '-m', 'selenoid', '-q',
                   '--junitxml=' + str(run / 'selenoid.xml'), '--alluredir=' + str(raw)]
        record['stages']['selenoid'] = execute(command, run / 'selenoid.log', env)
    record['regression_wall_seconds'] = time.perf_counter() - full_started
    command = [sys.executable, str(root / 'ci/history.py'), '--results', str(raw), '--build', str(args.build_start + number - 1)]
    if previous:
        command += ['--previous', str(previous)]
    subprocess.run(command, check=True, cwd=root, env=env)
    report = run / 'allure-report'
    execute([args.allure, 'generate', str(raw), '--clean', '-o', str(report)], run / 'allure.log', env)
    record['summary'] = json.loads((report / 'widgets/summary.json').read_text(encoding='utf-8'))['statistic']
    record['completed'] = datetime.now(timezone.utc).isoformat()
    (run / 'run.json').write_text(json.dumps(record, indent=2), encoding='utf-8')
    records.append(record)
    (output / 'runs.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
    previous = report
    print('Completed regression', number, record['summary'], flush=True)
sys.exit(0 if all(s['exit_code'] == 0 for r in records for s in r['stages'].values()) else 1)
