"""Enforce the assignment's separate C0/C1 thresholds."""
import json
from pathlib import Path
import sys

totals = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))['totals']
c0 = 100 * totals['covered_lines'] / totals['num_statements']
c1 = 100 * totals['covered_branches'] / totals['num_branches'] if totals['num_branches'] else 100
print(f'C0={c0:.2f}%, C1={c1:.2f}% (own educational model)')
assert c0 >= 90 and c1 >= 80, 'Assignment coverage thresholds not met'
