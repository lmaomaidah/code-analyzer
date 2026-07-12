"""
test_validator.py
Owner: Maidah (Security & QA Lead)
Week:  Week 1 core tests, Week 2 hardening tests

Tests for utils/validator.py.
Run with: python -m pytest tests/test_validator.py -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from unittest.mock import patch, Mock
import requests

from utils.validator import validate_input


# ── Happy path ────────────────────────────────────────────────────────────────

def test_valid_code_accepted():
    data = {"code": "print('hello world')"}
    valid, msg = validate_input(data)
    assert valid is True
    assert msg == ""


@patch("utils.validator.requests.head")
def test_valid_github_url_accepted(mock_head):
    mock_head.return_value = Mock(status_code=200)
    data = {"github_url": "https://github.com/psf/requests"}
    valid, msg = validate_input(data)
    assert valid is True


# ── Empty / missing input ─────────────────────────────────────────────────────

def test_empty_body_rejected():
    valid, msg = validate_input({})
    assert valid is False
    assert "code" in msg or "github_url" in msg


def test_both_fields_rejected():
    data = {"code": "print('hi')", "github_url": "https://github.com/user/repo"}
    valid, msg = validate_input(data)
    assert valid is False
    assert "not both" in msg


# ── Code length ───────────────────────────────────────────────────────────────

def test_code_too_short_rejected():
    data = {"code": "hi"}
    valid, msg = validate_input(data)
    assert valid is False
    assert "short" in msg.lower()


def test_code_at_max_length_accepted():
    data = {"code": "x = 1\n" * 8333}   # ~50,000 chars
    valid, msg = validate_input(data)
    assert valid is True


def test_code_over_max_length_rejected():
    data = {"code": "x" * 50_001}
    valid, msg = validate_input(data)
    assert valid is False
    assert "50,000" in msg or "maximum" in msg.lower()


# ── GitHub URL format ─────────────────────────────────────────────────────────

def test_github_url_wrong_prefix_rejected():
    data = {"github_url": "http://github.com/user/repo"}   # http not https
    valid, msg = validate_input(data)
    assert valid is False


def test_github_url_non_github_rejected():
    data = {"github_url": "https://gitlab.com/user/repo"}
    valid, msg = validate_input(data)
    assert valid is False


def test_github_url_with_subpath_rejected():
    data = {"github_url": "https://github.com/user/repo/tree/main/src"}
    valid, msg = validate_input(data)
    assert valid is False


def test_github_url_no_repo_rejected():
    data = {"github_url": "https://github.com/user"}
    valid, msg = validate_input(data)
    assert valid is False


# ── Type checking ─────────────────────────────────────────────────────────────

def test_code_not_string_rejected():
    data = {"code": 12345}
    valid, msg = validate_input(data)
    assert valid is False


def test_github_url_not_string_rejected():
    data = {"github_url": ["https://github.com/user/repo"]}
    valid, msg = validate_input(data)
    assert valid is False


# ── Week 2 · GitHub reachability check ────────────────────────────────────────
# We mock requests.head so the test suite never depends on network access
# or on a specific repo continuing to exist / stay public.

@patch("utils.validator.requests.head")
def test_github_url_404_rejected(mock_head):
    mock_head.return_value = Mock(status_code=404)
    data = {"github_url": "https://github.com/nonexistent-user-xyz/nonexistent-repo"}
    valid, msg = validate_input(data)
    assert valid is False
    assert "not reachable" in msg.lower() or "private" in msg.lower()


@patch("utils.validator.requests.head")
def test_github_url_private_repo_rejected(mock_head):
    # Private repos typically 404 to an unauthenticated request too, but
    # some setups return other non-200 codes — either way, reject.
    mock_head.return_value = Mock(status_code=403)
    data = {"github_url": "https://github.com/someuser/private-repo"}
    valid, msg = validate_input(data)
    assert valid is False


@patch("utils.validator.requests.head")
def test_github_url_network_error_rejected(mock_head):
    mock_head.side_effect = requests.ConnectionError("simulated network failure")
    data = {"github_url": "https://github.com/psf/requests"}
    valid, msg = validate_input(data)
    assert valid is False
    assert "connect" in msg.lower()


@patch("utils.validator.requests.head")
def test_github_url_timeout_rejected(mock_head):
    mock_head.side_effect = requests.Timeout("simulated timeout")
    data = {"github_url": "https://github.com/psf/requests"}
    valid, msg = validate_input(data)
    assert valid is False


# ── Week 2 · Expanded BLOCKED_PATTERNS ─────────────────────────────────────────
# Each new pattern gets a "blocked" test AND a "similar but safe" test, so we
# don't accidentally reject legitimate code that merely looks similar.

def test_blocked_import_subprocess_string():
    data = {"code": "mod = __import__('subprocess')\nmod.run(['ls'])"}
    valid, msg = validate_input(data)
    assert valid is False


def test_safe_normal_subprocess_import_not_blocked():
    # A plain top-level `import subprocess` (not the __import__ string form)
    # should NOT be blocked — Bandit itself only flags it as informational.
    data = {"code": "import subprocess\nprint('just importing, not calling')"}
    valid, msg = validate_input(data)
    assert valid is True


def test_blocked_exec_call():
    data = {"code": "user_code = 'print(1)'\nexec(user_code)"}
    valid, msg = validate_input(data)
    assert valid is False


def test_safe_word_containing_exec_not_blocked():
    # Words that merely *contain* "exec" shouldn't trip the exec() pattern.
    data = {"code": "def execute_plan():\n    return 'not a call to exec'"}
    valid, msg = validate_input(data)
    assert valid is True


def test_blocked_eval_call():
    data = {"code": "result = eval('1 + 1')\nprint(result)"}
    valid, msg = validate_input(data)
    assert valid is False


def test_safe_evaluate_word_not_blocked():
    # Note: deliberately avoids the literal substring "eval(" anywhere in
    # this sample, including in comments - the pattern is a dumb text match
    # and would (correctly) flag it even inside a comment.
    data = {"code": "def evaluate_score(x):\n    return x * 2"}
    valid, msg = validate_input(data)
    assert valid is True


def test_blocked_os_system_call():
    data = {"code": "import os\nos.system('rm -rf /')"}
    valid, msg = validate_input(data)
    assert valid is False


def test_safe_os_getcwd_not_blocked():
    data = {"code": "import os\nprint(os.getcwd())"}
    valid, msg = validate_input(data)
    assert valid is True


def test_blocked_shell_true():
    data = {"code": "import subprocess\nsubprocess.call('ls', shell=True)"}
    valid, msg = validate_input(data)
    assert valid is False


def test_safe_shell_false_not_blocked():
    data = {"code": "import subprocess\nsubprocess.call(['ls'], shell=False)"}
    valid, msg = validate_input(data)
    assert valid is True


def test_blocked_file_write_mode():
    data = {"code": "with open('/etc/passwd', 'w') as f:\n    f.write('pwned')"}
    valid, msg = validate_input(data)
    assert valid is False


def test_safe_file_read_mode_not_blocked():
    data = {"code": "with open('data.txt', 'r') as f:\n    contents = f.read()"}
    valid, msg = validate_input(data)
    assert valid is True
