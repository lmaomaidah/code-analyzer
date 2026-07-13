import pytest
from utils.github_fetcher import fetch_github_code

# ─── Test 1: Real public repo ───────────────────────────────
def test_real_repo_returns_code():
    """
    Test with a real small public repo that has .py files.
    Skips gracefully if GitHub rate limit is hit.
    """
    try:
        result = fetch_github_code("https://github.com/realpython/python-basics-exercises")
        assert isinstance(result, str)
        assert len(result) > 0
    except ValueError as e:
        if "rate limit" in str(e).lower():
            pytest.skip("GitHub rate limit hit — skipping test")
        raise

# ─── Test 2: Fake URL ────────────────────────────────────────
def test_fake_url_raises_error():
    """
    A URL that doesn't exist should raise ValueError.
    """
    with pytest.raises(ValueError):
        fetch_github_code("https://github.com/thisuser99999/thisrepo99999")

# ─── Test 3: Wrong repo ──────────────────────────────────────
def test_wrong_repo_raises_error():
    """
    A completely wrong URL should raise ValueError.
    """
    with pytest.raises(ValueError):
        fetch_github_code("https://github.com/aaaaa/bbbbb")

# ─── Test 4: Result under 50,000 chars ──────────────────────
def test_result_under_char_limit():
    """
    Result should never exceed 50,000 characters.
    Skips gracefully if GitHub rate limit is hit.
    """
    try:
        result = fetch_github_code("https://github.com/realpython/python-basics-exercises")
        assert len(result) <= 50000
    except ValueError as e:
        if "rate limit" in str(e).lower():
            pytest.skip("GitHub rate limit hit — skipping test")
        raise