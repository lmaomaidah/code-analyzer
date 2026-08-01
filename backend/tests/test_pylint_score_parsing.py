"""
test_pylint_score_parsing.py
Owner: Maidah (Security & QA Lead) — regression test for a bug found
during Week 5 integration testing.

Root cause: on at least one Windows/Python 3.13 environment, Pylint
3.2.5's text reporter wraps its score line WITHOUT a space between
"rated" and "at" (observed: "...has been ratedat 10.00/10..."). The
original score-extraction code did an exact substring match on
"Your code has been rated at", which silently never matched in that
case — Pylint's score stayed at 0.0 on every request, feeding directly
into compute_score() without ever raising an error. Nothing crashed;
the whole pipeline just quietly reported the wrong number.

This is exactly the kind of bug a "never crashes" test suite can miss,
since every existing test only checks "did it return 200 / did it not
error", not "is the number actually correct." These tests pin the
regex-based fix against the real buggy output, the normal-spaced form,
and negative-score edge cases, so this can't silently regress if the
score-parsing logic is ever touched again.

Run with: python -m pytest tests/test_pylint_score_parsing.py -v
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from analyzers.pylint_scanner import SCORE_PATTERN


def _extract(text: str):
    match = SCORE_PATTERN.search(text)
    return float(match.group(1)) if match else None


# ── The exact bug that was found ───────────────────────────────────────────────

def test_missing_space_ratedat_form_is_parsed():
    """
    The literal output captured from the affected Windows/Python 3.13
    environment. Before the fix, this returned None (no match), which
    silently became score=0.0.
    """
    text = (
        "\n--------------------------------------------------------------------\n"
        "Your code has been ratedat 10.00/10 (previous run: 10.00/10, +0.00)\n\n"
    )
    assert _extract(text) == 10.00


# ── The normal form, on environments where it isn't buggy ─────────────────────

def test_normal_spaced_form_still_parses():
    text = "Your code has been rated at 7.50/10 (previous run: 7.50/10, +0.00)"
    assert _extract(text) == 7.50


# ── Edge cases the fix must not break ──────────────────────────────────────────

def test_negative_score_parses():
    """Pylint can and does report negative scores for very bad code."""
    text = "Your code has been rated at -2.50/10"
    assert _extract(text) == -2.50


def test_zero_score_parses():
    text = "Your code has been rated at 0.00/10"
    assert _extract(text) == 0.00


def test_extra_whitespace_between_rated_and_at_parses():
    text = "Your code has been rated   at 9.13/10"
    assert _extract(text) == 9.13


def test_no_score_line_present_returns_none():
    """
    If Pylint's output genuinely doesn't contain a score line (e.g. a
    totally different failure), the pattern should not match garbage —
    confirms the regex isn't so loose it produces false positives.
    """
    text = "some unrelated pylint output with no score in it at all"
    assert _extract(text) is None