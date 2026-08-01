"""
diagnose_score.py
Run this from inside backend/, with the venv active, to see exactly how
compute_score() breaks down for the CLEAN_CODE sample from
test_integration.py. This isolates whether the low score is coming from
Pylint, Radon, or Bandit before we touch the test's threshold.

Usage (from backend/, venv active):
    python diagnose_score.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from analyzers.pylint_scanner import run_pylint
from analyzers.radon_scanner import run_radon
from analyzers.bandit_scanner import run_bandit
from app import compute_score

CLEAN_CODE = '''"""Small, well-documented arithmetic utility module."""


def add(a: int, b: int) -> int:
    """Return the sum of a and b."""
    return a + b


def multiply(a: int, b: int) -> int:
    """Return the product of a and b."""
    return a * b


def average(values: list) -> float:
    """Return the arithmetic mean of a list of numbers."""
    if not values:
        return 0.0
    return sum(values) / len(values)
'''

print("=" * 70)
print("PYLINT")
print("=" * 70)
p = run_pylint(CLEAN_CODE)
print(f"  score:  {p['score']}")
print(f"  issues: {p['issue_count']}")
for issue in p["issues"]:
    print(f"    - [{issue['severity']}] line {issue['line']}: {issue['message']} ({issue.get('symbol')})")
pylint_contribution = (p.get("score", 0.0) / 10.0) * 40
print(f"  --> contributes {pylint_contribution:.2f} / 40 to final score")

print()
print("=" * 70)
print("RADON")
print("=" * 70)
r = run_radon(CLEAN_CODE)
print(f"  maintainability_index: {r['maintainability_index']}")
print(f"  average_complexity:    {r['average_complexity']}")
print(f"  error:                 {r['error']}")
radon_contribution = (r.get("maintainability_index", 0.0) / 100.0) * 30
print(f"  --> contributes {radon_contribution:.2f} / 30 to final score")

print()
print("=" * 70)
print("BANDIT")
print("=" * 70)
b = run_bandit(CLEAN_CODE)
print(f"  high_count:   {b['high_count']}")
print(f"  medium_count: {b['medium_count']}")
print(f"  low_count:    {b['low_count']}")
print(f"  error:        {b['error']}")
bandit_contribution = max(0, 30 - (b.get("high_count", 0) * 10) - (b.get("medium_count", 0) * 5))
print(f"  --> contributes {bandit_contribution} / 30 to final score")

print()
print("=" * 70)
final = compute_score(p, r, b)
print(f"FINAL SCORE: {final}")
print("=" * 70)

print()
print(f"Pylint version resolved: ", end="")
os.system("pylint --version")
print(f"Radon version resolved: ", end="")
os.system("radon --version")
print(f"Bandit version resolved: ", end="")
os.system("bandit --version")