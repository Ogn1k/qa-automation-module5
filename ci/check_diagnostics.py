"""Verify screenshot/DOM capture for intentional setup and call failures.

This separate diagnostic probe never enters the product regression or its Pass Rate.
"""
import json
import argparse
from pathlib import Path
import subprocess
import sys

root = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--output', default='diagnostics')
args = parser.parse_args()
folder = root / 'results' / args.output
folder.mkdir(parents=True, exist_ok=True)
probe = folder / 'capture_probe.py'
probe.write_text('''import pytest

@pytest.fixture
def broken_setup(page):
    page.goto("data:text/html,<h1>Intentional setup failure</h1>")
    raise RuntimeError("Intentional setup diagnostic probe")

def test_setup_capture(broken_setup):
    pass

def test_call_capture(page):
    page.goto("data:text/html,<h1>Intentional assertion failure</h1>")
    assert False, "Intentional call diagnostic probe"
''', encoding='utf-8')
raw = folder / 'allure-results'
if raw.exists():
    raise SystemExit('Diagnostic evidence already exists; choose a fresh output directory')
command = [sys.executable, '-m', 'pytest', str(probe), '-q', '--tb=short',
           '--alluredir=' + str(raw), '--junitxml=' + str(folder / 'probe.xml')]
result = subprocess.run(command, cwd=root, capture_output=True, text=True)
(folder / 'probe.log').write_text(result.stdout + result.stderr, encoding='utf-8')
results = [json.loads(p.read_text(encoding='utf-8')) for p in raw.glob('*-result.json')]
attachments = []


def collect(value):
    if isinstance(value, dict):
        attachments.extend(value.get('attachments', []))
        for key, child in value.items():
            if key != 'attachments':
                collect(child)
    elif isinstance(value, list):
        for child in value:
            collect(child)


for file in raw.glob('*.json'):
    collect(json.loads(file.read_text(encoding='utf-8')))
counts = {name: sum(a['name'] == name and (raw / a['source']).is_file() for a in attachments)
          for name in ['URL', 'Failure', 'DOM']}
assert result.returncode == 1 and len(results) == 2, 'Expected exactly two intentional failures'
assert all(count == 2 for count in counts.values()), counts
evidence = {'status': 'passed', 'expected_pytest_exit_code': 1,
            'intentional_probes': 2, 'attachments': counts,
            'excluded_from_product_regression': True}
(folder / 'verification.json').write_text(json.dumps(evidence, indent=2), encoding='utf-8')
print(json.dumps(evidence))
