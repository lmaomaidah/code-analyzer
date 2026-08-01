"""
test_edge_cases.py
Owner: Maidah (Security & QA Lead)
Week:  Week 5 — crash resilience and boundary testing

Every case here is something a real user (or an attacker probing the
server) could plausibly send. The one invariant that matters across all
of them: the server NEVER returns a 500. A bad or hostile input should
always come back as a clean 4xx with a useful error message, not a stack
trace or a crashed dyno on the free tier.

Each test below corresponds 1:1 to a bullet in the Week 5 sprint task
("submit an empty string, submit a string of random characters that
isn't Python, submit a file at exactly the 50,000 character limit,
submit a file one character over the limit, submit a GitHub URL for a
repo that has been deleted, submit a GitHub URL for a repo with zero
Python files"). Results are also summarised as a table in
SECURITY_AUDIT.md so they're visible without reading test code.

Run with: python -m pytest tests/test_edge_cases.py -v
"""

import sys
import os
from unittest.mock import patch, Mock

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ── 1. Empty string ────────────────────────────────────────────────────────────

def test_empty_string_code_never_500(client):
    """
    KNOWN QUIRK (documented, not a bug fix in scope this week): an empty
    string is falsy in Python, so validate_input()'s "was anything
    provided at all" check fires before the "too short" check does. The
    error message therefore says "provide either code or github_url"
    rather than "code is too short" — slightly misleading copy, but the
    request is still safely rejected with a 422, never a crash. Flagging
    this here so it isn't silently relied upon or "fixed" without
    updating this test.
    """
    resp = client.post("/analyze", json={"code": ""})
    assert resp.status_code == 422
    assert "error" in resp.get_json()


# ── 2. Non-Python garbage that still meets the length minimum ─────────────────

def test_random_garbage_non_python_never_500(client):
    """
    Not valid Python at all. Pylint should report a syntax error as an
    issue (not crash), Radon should fail gracefully on its own parse
    attempt, and Bandit should do the same — the endpoint should still
    return 200 with each tool's own `error` field populated as needed,
    per validation_rules.md's documented scope ("whether submitted code
    is syntactically valid Python is out of scope for input validation
    — Pylint handles this gracefully").
    """
    garbage = "@#$%^&*() not python at all {{{ ]][[ 12345 !!??"
    resp = client.post("/analyze", json={"code": garbage})
    assert resp.status_code in (200, 422)
    assert resp.status_code != 500


# ── 3 & 4. Length boundary: exactly at limit, and one over ────────────────────

def test_code_exactly_at_max_length_accepted(client):
    code = "x = 1\n" * 8333  # ~50,000 chars, mirrors test_validator.py's case
    assert len(code) <= 50_000
    resp = client.post("/analyze", json={"code": code})
    assert resp.status_code == 200


def test_code_one_over_max_length_rejected(client):
    code = "x" * 50_001
    resp = client.post("/analyze", json={"code": code})
    assert resp.status_code == 422
    body = resp.get_json()
    assert "50,000" in body["error"] or "maximum" in body["error"].lower()


# ── 5. GitHub URL pointing at a deleted / nonexistent repo ────────────────────

@patch("utils.validator.requests.head")
def test_deleted_github_repo_never_500(mock_head):
    mock_head.return_value = Mock(status_code=404)
    app.config["TESTING"] = True
    with app.test_client() as c:
        resp = c.post(
            "/analyze",
            json={"github_url": "https://github.com/deleted-user-xyz/deleted-repo"},
        )
    assert resp.status_code == 422
    assert "error" in resp.get_json()


# ── 6. GitHub URL for a repo that has zero .py files at all ───────────────────

@patch("utils.validator.requests.head")
@patch("utils.github_fetcher.requests.get")
def test_github_repo_with_zero_py_files_rejected_cleanly(mock_get, mock_head):
    """
    The validator's reachability check passes (repo exists, is public),
    but github_fetcher.fetch_github_code() finds nothing to analyse. This
    must surface as a clear 422, not a 200 with an empty/zero score and
    not a 500 from an unhandled empty-list edge case.
    """
    mock_head.return_value = Mock(status_code=200)

    empty_contents_response = Mock(status_code=200)
    empty_contents_response.json.return_value = []  # no files/folders at all
    mock_get.return_value = empty_contents_response

    app.config["TESTING"] = True
    with app.test_client() as c:
        resp = c.post(
            "/analyze",
            json={"github_url": "https://github.com/someuser/no-python-here"},
        )

    assert resp.status_code == 422
    body = resp.get_json()
    assert "error" in body
    assert ".py" in body["error"] or "no" in body["error"].lower()


# ── Blanket sweep: none of the above should ever 500 ──────────────────────────

@pytest.mark.parametrize(
    "payload",
    [
        {"code": ""},
        {"code": "@#$%^&*() not python at all {{{ ]][[ 12345 !!??"},
        {"code": "x" * 50_001},
        {"github_url": "not-even-a-url"},
        {"github_url": "https://gitlab.com/user/repo"},
        {},
    ],
)
def test_hostile_or_malformed_inputs_never_crash_server(client, payload):
    resp = client.post("/analyze", json=payload)
    assert resp.status_code != 500, (
        f"Payload {payload!r} caused a 500 — this must always fail "
        f"cleanly with a 4xx, never crash the server."
    )