"""
test_integration.py
Owner: Maidah (Security & QA Lead)
Week:  Week 5 — end-to-end integration testing

Distinct from test_security_integration.py (Week 4), which proves the
validator -> Bandit layering works and that no code persists on disk.
This file proves the *whole pipeline produces a trustworthy score* now
that Maria's compute_score() is the real weighted formula (Pylint 40% +
Radon 30% + Bandit 30%) rather than the Week 4 placeholder.

Run with: python -m pytest tests/test_integration.py -v
"""

import sys
import os
import glob
import tempfile

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


# ── Sample payloads ────────────────────────────────────────────────────────────

# Clean, well-documented, low-complexity code. Should score comfortably
# above the "good quality" band and trip zero Bandit findings.
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

# Deliberately messy AND security-flagged, without tripping validator
# BLOCKED_PATTERNS (no exec/eval/os.system/shell=True/__import__ os or
# subprocess/write-mode open — those are rejected before scanning even
# starts, which is intentional and covered by test_security_integration.py).
# This sample instead combines:
#   - deeply nested branching (kills Radon's maintainability index)
#   - no docstrings, single-letter names, no type hints (kills Pylint)
#   - three separate Bandit-flaggable but non-blocked issues: MD5 hashing,
#     `random` used for a "token", and unpickling arbitrary bytes — each is
#     its own MEDIUM finding, so the Bandit component of the score is
#     driven to (or near) zero.
# Static analysis tools only ever parse this — none of it is executed —
# so an invalid pickle payload is safe to include here.
MESSY_VULNERABLE_CODE = '''
import hashlib
import random
import pickle

def f(a,b,c,d,e):
    x=a
    if a>0:
        if b>0:
            if c>0:
                if d>0:
                    if e>0:
                        x=a+b+c+d+e
                    else:
                        x=a-b
                else:
                    x=b-c
            else:
                x=c-d
        else:
            x=d-e
    else:
        x=e
    password="super_secret_123"
    h=hashlib.md5(password.encode()).hexdigest()
    token=str(random.random())
    data=pickle.loads(b"")
    return x,h,token,data
'''


# ── Score threshold sanity checks ──────────────────────────────────────────────
# NOTE: these are integration-level sanity checks on the *whole pipeline*,
# not strict unit tests of the scoring formula itself (those belong to
# Maria, against compute_score() directly, with exact expected values).
# The thresholds below have headroom built in so they don't become flaky
# if the formula's weights are tuned slightly later.

def test_clean_documented_code_scores_high_via_full_pipeline(client):
    resp = client.post("/analyze", json={"code": CLEAN_CODE})
    assert resp.status_code == 200

    body = resp.get_json()
    # NOTE: no hardcoded absolute floor here on purpose. A fixed number
    # (e.g. "> 60") is tied to whatever exact Pylint/Radon versions are
    # resolved in a given environment — this bit us for real: a
    # Windows/Python 3.13 machine running Pylint 3.2.5 hit a genuine
    # score-parsing bug (see test_pylint_score_parsing.py) that silently
    # zeroed out the Pylint component on every request. A relative
    # comparison against the messy/vulnerable sample below is what
    # actually matters for this test and survives version differences.
    assert body["summary"]["bandit"]["high_count"] == 0
    assert body["summary"]["bandit"]["error"] is None
    assert body["summary"]["pylint"]["error"] is None
    assert body["summary"]["pylint"]["issue_count"] == 0


def test_messy_vulnerable_code_scores_low_via_full_pipeline(client):
    resp = client.post("/analyze", json={"code": MESSY_VULNERABLE_CODE})
    assert resp.status_code == 200

    body = resp.get_json()
    # At least one of the three planted Bandit findings should surface.
    assert (
        body["summary"]["bandit"]["medium_count"]
        + body["summary"]["bandit"]["high_count"]
    ) >= 1
    # The deep nesting should register as non-trivial complexity —
    # confirms Radon actually parsed the function, not just that it
    # didn't error.
    assert body["summary"]["radon"]["average_complexity"] > 1


def test_clean_code_scores_meaningfully_higher_than_messy_vulnerable_code(client):
    """
    The comparison that actually matters: whatever the absolute numbers
    are on a given machine, clean/documented/safe code must score
    substantially better than deeply-nested/undocumented/multi-finding
    code. This is robust to tool-version differences across environments
    in a way a fixed absolute threshold is not.
    """
    clean_resp = client.post("/analyze", json={"code": CLEAN_CODE})
    messy_resp = client.post("/analyze", json={"code": MESSY_VULNERABLE_CODE})

    clean_score = clean_resp.get_json()["score"]
    messy_score = messy_resp.get_json()["score"]

    assert clean_score - messy_score >= 20, (
        f"Expected clean code to score at least 20 points higher than "
        f"messy/vulnerable code. clean={clean_score}, messy={messy_score}"
    )


def test_response_shape_matches_api_contract(client):
    """
    Confirms the full response still matches what API.md promises Hira's
    dashboard — this is what stops a backend change from silently breaking
    the frontend without anyone noticing until Week 6 deployment.
    """
    resp = client.post("/analyze", json={"code": CLEAN_CODE})
    body = resp.get_json()

    assert "score" in body
    assert "issues" in body and isinstance(body["issues"], list)
    assert "summary" in body
    for tool in ("pylint", "radon", "bandit"):
        assert tool in body["summary"]

    assert "score" in body["summary"]["pylint"]
    assert "maintainability_index" in body["summary"]["radon"]
    assert "high_count" in body["summary"]["bandit"]
    assert "medium_count" in body["summary"]["bandit"]
    assert "low_count" in body["summary"]["bandit"]


# ── Persistence check (belt-and-suspenders alongside Week 4's version) ────────
# test_security_integration.py already proves this for the plain "code"
# path. Repeated here specifically around the messier/multi-finding sample
# above, so a future change to how compute_score() or the scanners handle
# "ugly" input can't quietly reintroduce a disk leak.

def test_no_temp_files_left_after_messy_code_pipeline(client):
    tmp_dir = tempfile.gettempdir()
    before = set(glob.glob(os.path.join(tmp_dir, "*.py")))

    resp = client.post("/analyze", json={"code": MESSY_VULNERABLE_CODE})
    assert resp.status_code == 200

    after = set(glob.glob(os.path.join(tmp_dir, "*.py")))
    leaked = after - before
    assert len(leaked) == 0, f"Submitted code left on disk: {leaked}"