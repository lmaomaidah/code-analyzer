"""
test_bandit_scanner.py
Owner: Maidah (Security & QA Lead)
Week:  Stubs in Week 1, real tests enabled in Week 3

Tests for analyzers/bandit_scanner.py.
Run with: python -m pytest tests/test_bandit_scanner.py -v
"""

import sys
import os
import glob
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from analyzers.bandit_scanner import run_bandit


# ── Structural tests (return shape, present since Week 1) ─────────────────────

def test_run_bandit_returns_dict():
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


def test_run_bandit_counts_are_integers():
    result = run_bandit("x = 1 + 2  # a simple expression")
    assert isinstance(result["high_count"],   int)
    assert isinstance(result["medium_count"], int)
    assert isinstance(result["low_count"],    int)


def test_run_bandit_issues_is_list():
    result = run_bandit("x = 1 + 2  # a simple expression")
    assert isinstance(result["issues"], list)


# ── Test code samples ─────────────────────────────────────────────────────────

SAFE_CODE = """
def add(a, b):
    \"\"\"Returns the sum of a and b.\"\"\"
    return a + b

def greet(name):
    return f"Hello, {name}!"
"""

VULNERABLE_CODE = """
import subprocess
user_input = input("Enter a command: ")
subprocess.call(user_input, shell=True)
"""

HARDCODED_SECRET = """
import hashlib

password = "super_secret_123"
hashed = hashlib.md5(password.encode()).hexdigest()
print(hashed)
"""

WEAK_CRYPTO = """
import random

def generate_session_token():
    return str(random.random())
"""


# ── Real tests (Week 3 — run_bandit is now fully implemented) ─────────────────

def test_safe_code_has_no_high_severity():
    result = run_bandit(SAFE_CODE)
    assert result["error"] is None
    assert result["high_count"] == 0


def test_shell_injection_detected():
    """B602: subprocess call with shell=True should be HIGH severity."""
    result = run_bandit(VULNERABLE_CODE)
    assert result["high_count"] >= 1
    assert any("shell" in i["message"].lower() for i in result["issues"])


def test_hardcoded_secret_detected():
    """B105/B106/B324: hardcoded password + weak hash should surface as issues."""
    result = run_bandit(HARDCODED_SECRET)
    assert result["medium_count"] >= 1 or result["high_count"] >= 1


def test_weak_crypto_detected():
    """B311: Python's random module is not safe for security-sensitive values."""
    result = run_bandit(WEAK_CRYPTO)
    assert len(result["issues"]) >= 1
    assert result["error"] is None


def test_issues_have_required_fields():
    """Every issue dict must have the fields the dashboard depends on."""
    result = run_bandit(VULNERABLE_CODE)
    assert len(result["issues"]) > 0
    for issue in result["issues"]:
        assert "tool"       in issue
        assert "severity"   in issue
        assert "message"    in issue
        assert "line"       in issue
        assert issue["tool"] == "bandit"


def test_severity_values_are_valid():
    result = run_bandit(VULNERABLE_CODE)
    valid_severities = {"HIGH", "MEDIUM", "LOW"}
    for issue in result["issues"]:
        assert issue["severity"] in valid_severities


def test_error_is_none_on_success():
    result = run_bandit(SAFE_CODE)
    assert result["error"] is None


def test_temp_file_is_deleted_after_scan():
    """SECURITY: no user code should remain on disk after the scan."""
    before = set(glob.glob(os.path.join(_temp_dir(), "*.py")))
    run_bandit(VULNERABLE_CODE)
    after = set(glob.glob(os.path.join(_temp_dir(), "*.py")))
    new_files = after - before
    assert len(new_files) == 0, f"Temp files not cleaned up: {new_files}"


def test_temp_file_deleted_even_when_bandit_errors():
    """SECURITY: cleanup must happen in a `finally`, not only on the happy path."""
    import unittest.mock as mock
    import subprocess as sp

    before = set(glob.glob(os.path.join(_temp_dir(), "*.py")))

    with mock.patch(
        "analyzers.bandit_scanner.subprocess.run",
        side_effect=sp.TimeoutExpired(cmd="bandit", timeout=15),
    ):
        result = run_bandit(SAFE_CODE)

    after = set(glob.glob(os.path.join(_temp_dir(), "*.py")))
    assert result["error"] is not None
    assert len(after - before) == 0, "Temp file leaked when Bandit itself failed"


def _temp_dir():
    import tempfile as _t
    return _t.gettempdir()