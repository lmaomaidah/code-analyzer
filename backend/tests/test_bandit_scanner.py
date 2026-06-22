"""
test_bandit_scanner.py
Owner: Maidah (Security & QA Lead)
Week:  Stubs in Week 1, real tests in Week 3 when scanner is implemented

Tests for analyzers/bandit_scanner.py.
Run with: python -m pytest tests/test_bandit_scanner.py -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from analyzers.bandit_scanner import run_bandit


# ── Stub tests (pass now, prove the module loads) ─────────────────────────────

def test_run_bandit_returns_dict():
    """Confirm run_bandit() returns a dict — even while it's a stub."""
    result = run_bandit("print('hello')")
    assert isinstance(result, dict)


def test_run_bandit_has_expected_keys():
    """Confirm the return dict has the keys the rest of the app expects."""
    result = run_bandit("x = 1")
    assert "issues"       in result
    assert "high_count"   in result
    assert "medium_count" in result
    assert "low_count"    in result
    assert "error"        in result


# ── Real tests (uncomment in Week 3 when run_bandit is implemented) ───────────

SAFE_CODE = """
def add(a, b):
    return a + b
"""

VULNERABLE_CODE = """
import subprocess
user_input = input("cmd: ")
subprocess.call(user_input, shell=True)
"""

HARDCODED_SECRET = """
import hashlib
password = "super_secret_123"
hashed = hashlib.md5(password.encode()).hexdigest()
"""

# def test_safe_code_has_no_high_severity():
#     result = run_bandit(SAFE_CODE)
#     assert result["high_count"] == 0
#     assert result["error"] is None

# def test_shell_injection_detected():
#     result = run_bandit(VULNERABLE_CODE)
#     assert result["high_count"] >= 1
#     assert any("shell" in i["message"].lower() for i in result["issues"])

# def test_hardcoded_secret_detected():
#     result = run_bandit(HARDCODED_SECRET)
#     assert result["medium_count"] >= 1 or result["high_count"] >= 1

# def test_empty_code_does_not_crash():
#     result = run_bandit("")
#     assert result["error"] is not None or result["issues"] == []

# def test_temp_file_is_deleted_after_scan():
#     import glob
#     run_bandit(VULNERABLE_CODE)
#     tmp_files = glob.glob("/tmp/bandit_*.py")
#     assert len(tmp_files) == 0
