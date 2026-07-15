import pytest
from analyzers.radon_scanner import run_radon

# ─── Test 1: Simple code returns result ──────────────────────
def test_simple_code_returns_result():
    """Simple function should return valid result."""
    code = '''
def add(a, b):
    return a + b
'''
    result = run_radon(code)
    assert isinstance(result, dict)
    assert "average_complexity" in result
    assert "maintainability_index" in result
    assert "functions" in result
    assert result["error"] is None

# ─── Test 2: Function detected ───────────────────────────────
def test_function_detected():
    """Radon should detect functions and their complexity."""
    code = '''
def add(a, b):
    return a + b
'''
    result = run_radon(code)
    assert len(result["functions"]) > 0
    assert result["functions"][0]["name"] == "add"

# ─── Test 3: Complex code has higher complexity ───────────────
def test_complex_code_higher_complexity():
    """Code with many if/else should have higher complexity."""
    simple_code = '''
def add(a, b):
    return a + b
'''
    complex_code = '''
def check(a, b, c):
    if a > 0:
        if b > 0:
            if c > 0:
                return 1
            else:
                return 2
        else:
            return 3
    else:
        return 4
'''
    simple = run_radon(simple_code)
    complex_ = run_radon(complex_code)
    assert complex_["average_complexity"] > simple["average_complexity"]

# ─── Test 4: Maintainability index is valid ──────────────────
def test_maintainability_index_range():
    """Maintainability index should be between 0 and 100."""
    code = '''
def add(a, b):
    return a + b
'''
    result = run_radon(code)
    assert 0 <= result["maintainability_index"] <= 100

# ─── Test 5: Empty code no crash ─────────────────────────────
def test_empty_code_no_crash():
    """Empty string should not crash the scanner."""
    result = run_radon("")
    assert isinstance(result, dict)
    assert "error" in result