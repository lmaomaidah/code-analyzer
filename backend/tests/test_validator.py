"""
test_validator.py
Owner: Maidah (Security & QA Lead)
Week:  Week 1

Tests for utils/validator.py.
Run with: python -m pytest tests/test_validator.py -v
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils.validator import validate_input


# ── Happy path ────────────────────────────────────────────────────────────────

def test_valid_code_accepted():
    data = {"code": "print('hello world')"}
    valid, msg = validate_input(data)
    assert valid is True
    assert msg == ""


def test_valid_github_url_accepted():
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
