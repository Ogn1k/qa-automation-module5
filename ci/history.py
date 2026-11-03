"""Prepare Allure 2 metadata and carry only the previous report's history."""
import argparse
import json
from pathlib import Path
import shutil

parser = argparse.ArgumentParser()
parser.add_argument('--results', required=True)
parser.add_argument('--previous')
parser.add_argument('--build', type=int, required=True)
parser.add_argument('--url', default='')
args = parser.parse_args()
results = Path(args.results)
results.mkdir(parents=True, exist_ok=True)
if args.previous:
    previous = Path(args.previous) / 'history'
    if previous.is_dir():
        shutil.copytree(previous, results / 'history', dirs_exist_ok=True)
executor = {'name': 'Module 5 regression', 'type': 'github' if args.url else 'local',
            'buildOrder': args.build, 'buildName': f'Regression {args.build}',
            'buildUrl': args.url, 'reportUrl': args.url}
(results / 'executor.json').write_text(json.dumps(executor, indent=2), encoding='utf-8')
(results / 'categories.json').write_text(json.dumps([
    {'name': 'Assertion failures', 'matchedStatuses': ['failed']},
    {'name': 'Environment or fixture errors', 'matchedStatuses': ['broken']}
], indent=2), encoding='utf-8')
