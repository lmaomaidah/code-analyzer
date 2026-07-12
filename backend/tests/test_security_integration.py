"""
test_security_integration.py
Owner: Maidah (Security & QA Lead)
Week:  Week 4 — end-to-end security + integration testing

These tests hit the real /analyze endpoint (via Flask's test client) rather
than calling run_bandit()/validate_input() directly, to confirm the whole
request path behaves correctly for security-relevant inputs — not just the
individual functions in isolation.

Run with: python -m pytest tests/test_security_integration.py -v
"""

import sys
import os
import glob
import tempfile
from unittest.mock import patch, Mock

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ── Sample payloads ────────────────────────────────────────────────────────────

# NOTE: this sample deliberately does NOT use shell=True, os.system(),
# exec(), eval(), or a write-mode open() — those are all in
# validator.BLOCKED_PATTERNS as of Week 2, so code containing them gets
# rejected with a 422 before it ever reaches Bandit. That's the *validator*
# doing its job. To exercise the Bandit path specifically, this sample uses
# a weak-hash vulnerability (B324) instead, which BLOCKED_PATTERNS doesn't
# (and shouldn't) cover — hashing isn't inherently dangerous the way
# exec/eval/shell=True are, it's just the wrong algorithm choice, which is
# exactly the kind of thing Bandit (not the validator) is meant to catch.
VULNERABLE_CODE = """
import hashlib

password = "super_secret_123"
hashed = hashlib.md5(password.encode()).hexdigest()
"""

# This one WOULD trigger real Bandit findings (shell injection) but is
# blocked at the validator layer first — used below to confirm that
# layering explicitly rather than let it silently mask the Bandit test.
SHELL_INJECTION_CODE = """
import subprocess
user_input = input("Enter a command: ")
subprocess.call(user_input, shell=True)
"""

SAFE_CODE = """
def add(a, b):
    return a + b
"""

BLOCKED_CODE = "os.system('whoami')"  # trips BLOCKED_PATTERNS before it ever
                                       # reaches the scanners


# ── Known-vulnerable code end-to-end ───────────────────────────────────────────

def test_vulnerable_code_flagged_by_bandit_via_api(client):
    """
    Submitting known-vulnerable code through the real /analyze endpoint
    should surface Bandit's finding in the response, not just when calling
    run_bandit() directly.
    """
    resp = client.post("/analyze", json={"code": VULNERABLE_CODE})
    assert resp.status_code == 200

    body = resp.get_json()
    bandit_summary = body["summary"]["bandit"]

    assert bandit_summary["error"] is None
    assert bandit_summary["high_count"] >= 1
    assert any(i["tool"] == "bandit" for i in body["issues"])
    assert any("md5" in i["message"].lower() for i in body["issues"])


def test_shell_injection_sample_caught_by_validator_not_bandit(client):
    """
    Confirms the two security layers stack the way they're supposed to:
    obviously dangerous constructs (shell=True) never even reach Bandit
    because the validator rejects them first.
    """
    resp = client.post("/analyze", json={"code": SHELL_INJECTION_CODE})
    assert resp.status_code == 422


def test_safe_code_has_no_bandit_issues_via_api(client):
    resp = client.post("/analyze", json={"code": SAFE_CODE})
    assert resp.status_code == 200
    assert resp.get_json()["summary"]["bandit"]["high_count"] == 0


def test_blocked_pattern_rejected_before_scanning(client):
    """
    Input that trips BLOCKED_PATTERNS should be rejected by the validator
    with a 422 and never reach the scanners at all.
    """
    resp = client.post("/analyze", json={"code": BLOCKED_CODE})
    assert resp.status_code == 422
    assert "blocked pattern" in resp.get_json()["error"].lower()


# ── KNOWN LIMITATION — documented, not silently skipped ────────────────────────
#
# The task list also asks us to verify that the vulnerable-code response gets
# an "appropriately low" score. We can't assert on that yet: compute_score()
# in app.py is still the Week 4 placeholder (`return 75`) regardless of what
# Bandit/Pylint find — that formula is Maria's Week 4 deliverable. Once it's
# implemented, uncomment the test below.

# def test_vulnerable_code_produces_low_score(client):
#     resp = client.post("/analyze", json={"code": VULNERABLE_CODE})
#     assert resp.get_json()["score"] < 50


# ── No code persists on disk after a request completes ────────────────────────

def test_no_temp_files_left_after_analyze_request(client):
    """
    SECURITY: after a full /analyze round trip (validation -> bandit ->
    response), no file derived from the submitted code should still be on
    disk. This is the same guarantee test_bandit_scanner.py checks at the
    unit level, repeated here at the API level so a future change to app.py
    (e.g. writing code to disk before calling scanners) can't silently
    reintroduce a leak.
    """
    tmp_dir = tempfile.gettempdir()
    before = set(glob.glob(os.path.join(tmp_dir, "*.py")))

    resp = client.post("/analyze", json={"code": VULNERABLE_CODE})
    assert resp.status_code == 200

    after = set(glob.glob(os.path.join(tmp_dir, "*.py")))
    leaked = after - before
    assert len(leaked) == 0, f"Submitted code left on disk: {leaked}"


def test_no_temp_files_left_even_when_bandit_fails(client):
    """Cleanup must hold even when the scanner itself errors out."""
    tmp_dir = tempfile.gettempdir()
    before = set(glob.glob(os.path.join(tmp_dir, "*.py")))

    with patch(
        "analyzers.bandit_scanner.subprocess.run",
        side_effect=Exception("simulated bandit crash"),
    ):
        # run_bandit only catches subprocess.TimeoutExpired/FileNotFoundError
        # explicitly, so a generic Exception here is expected to propagate
        # as a 500 — the point of this test is that the temp file is still
        # cleaned up by the `finally` block regardless.
        try:
            client.post("/analyze", json={"code": VULNERABLE_CODE})
        except Exception:
            pass

    after = set(glob.glob(os.path.join(tmp_dir, "*.py")))
    leaked = after - before
    assert len(leaked) == 0, f"Submitted code left on disk after a crash: {leaked}"


# ── GitHub URL path stays validated end-to-end ─────────────────────────────────

@patch("utils.validator.requests.head")
def test_unreachable_github_url_rejected_via_api(mock_head):
    mock_head.return_value = Mock(status_code=404)
    app.config["TESTING"] = True
    with app.test_client() as c:
        resp = c.post(
            "/analyze",
            json={"github_url": "https://github.com/nonexistent/nonexistent"},
        )
    assert resp.status_code == 422
