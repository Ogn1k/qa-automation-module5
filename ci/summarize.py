"""Write actual JUnit results to the GitHub Actions job summary."""
import os
from pathlib import Path
import xml.etree.ElementTree as ET

lines = ['## Test results', '', '| Report | Total | Passed | Failed | Errors | Skipped |',
         '|---|---:|---:|---:|---:|---:|']
files = sorted(Path('results').rglob('*.xml'))
for path in files:
    root = ET.parse(path).getroot()
    cases = list(root.iter('testcase'))
    failed = sum(case.find('failure') is not None for case in cases)
    errors = sum(case.find('error') is not None for case in cases)
    skipped = sum(case.find('skipped') is not None for case in cases)
    passed = len(cases) - failed - errors - skipped
    lines.append(f'| {path.as_posix()} | {len(cases)} | {passed} | {failed} | {errors} | {skipped} |')
if not files:
    lines += ['', 'No JUnit report was generated. Check dependency installation and test logs.']
text = '\n'.join(lines) + '\n'
print(text)
destination = os.environ.get('GITHUB_STEP_SUMMARY')
if destination:
    with open(destination, 'a', encoding='utf-8') as output:
        output.write(text)
