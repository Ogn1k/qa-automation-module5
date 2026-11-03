"""Try the configured mirror first, then an explicit primary-source fallback."""
import json
import os
from pathlib import Path
import subprocess
import sys
from datetime import datetime, timezone

root = Path(__file__).resolve().parents[1]
evidence = root / 'results' / 'dependency-install.json'
evidence.parent.mkdir(parents=True, exist_ok=True)
indexes = [os.getenv('MODULE5_PYPI_MIRROR', 'https://pypi-mirror.gitverse.ru/simple/'),
           'https://pypi.org/simple/']
requirements = root / 'requirements.lock.txt'
if not requirements.exists():
    requirements = root / 'requirements.txt'
attempts = []
for index in indexes:
    command = [sys.executable, '-m', 'pip', 'install', '--disable-pip-version-check',
               '--retries', '0', '--timeout', '20', '--index-url', index,
               '-r', str(requirements)]
    result = subprocess.run(command, cwd=root, capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr, file=sys.stderr)
    attempts.append({'index': index, 'exit_code': result.returncode,
                     'stdout': result.stdout, 'stderr': result.stderr})
    if result.returncode == 0:
        break
evidence.write_text(json.dumps({'timestamp': datetime.now(timezone.utc).isoformat(),
                               'attempts': attempts}, ensure_ascii=False, indent=2), encoding='utf-8')
sys.exit(result.returncode)
