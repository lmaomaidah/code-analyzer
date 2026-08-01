"""
diagnose_pylint.py
Follow-up to diagnose_score.py — that script showed Pylint returning a
score of 0.0 with zero issues, which is the exact shape run_pylint()
falls back to on an internal exception, but it didn't print the error
message that would explain WHY. This script prints that, plus the raw
subprocess output, directly.

Usage (from backend/, venv active):
    python diagnose_pylint.py
"""

import sys
import os
import subprocess
import tempfile

sys.path.insert(0, os.path.dirname(__file__))

from analyzers.pylint_scanner import run_pylint

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
print("STEP 1 — full run_pylint() return value, including 'error'")
print("=" * 70)
result = run_pylint(CLEAN_CODE)
for k, v in result.items():
    print(f"  {k}: {v!r}")

print()
print("=" * 70)
print("STEP 2 — raw subprocess calls, exactly as run_pylint() makes them")
print("=" * 70)

tmp_path = None
try:
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(CLEAN_CODE)
        tmp_path = tmp.name

    print(f"Temp file written to: {tmp_path}")
    print()

    json_result = subprocess.run(
        ["pylint", tmp_path, "--output-format=json"],
        capture_output=True, text=True,
    )
    print(f"[json call] returncode: {json_result.returncode}")
    print(f"[json call] stdout: {json_result.stdout!r}")
    print(f"[json call] stderr: {json_result.stderr!r}")
    print()

    score_result = subprocess.run(
        ["pylint", tmp_path, "--output-format=text", "--score=yes"],
        capture_output=True, text=True,
    )
    print(f"[score call] returncode: {score_result.returncode}")
    print(f"[score call] stdout: {score_result.stdout!r}")
    print(f"[score call] stderr: {score_result.stderr!r}")

finally:
    if tmp_path and os.path.exists(tmp_path):
        os.unlink(tmp_path)