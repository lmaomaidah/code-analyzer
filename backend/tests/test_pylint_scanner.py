import pytest
from analyzers.pylint_scanner import run_pylint

# ─── Test 1: Good code ───────────────────────────────────────
def test_good_code_returns_result():
    """Clean code should return a result with no errors."""
    code = '''
def add(a, b):
    """Add two numbers."""
    return a + b
'''
    result = run_pylint(code)
    assert isinstance(result, dict)
    assert "score" in result
    assert "issues" in result
    assert result["error"] is None

# ─── Test 2: Bad code has issues ─────────────────────────────
def test_bad_code_returns_issues():
    """Bad code should return issues."""
    code = '''
def c(a,b):
    x=a+b
    return x
'''
    result = run_pylint(code)
    assert result["issue_count"] > 0
    assert len(result["issues"]) > 0

# ─── Test 3: Issues have correct structure ───────────────────
def test_issues_have_correct_structure():
    """Each issue should have tool, severity, message, line."""
    code = '''
def c(a,b):
    return a+b
'''
    result = run_pylint(code)
    if result["issues"]:
        issue = result["issues"][0]
        assert "tool" in issue
        assert "severity" in issue
        assert "message" in issue
        assert "line" in issue
        assert issue["tool"] == "pylint"

# ─── Test 4: Severity values are valid ───────────────────────
def test_severity_values_are_valid():
    """Severity must be HIGH, MEDIUM, or LOW."""
    code = '''
def c(a,b):
    return a+b
'''
    result = run_pylint(code)
    valid = {"HIGH", "MEDIUM", "LOW"}
    for issue in result["issues"]:
        assert issue["severity"] in valid

# ─── Test 5: Empty code handled gracefully ───────────────────
def test_empty_code_no_crash():
    """Empty string should not crash the scanner."""
    result = run_pylint("")
    assert isinstance(result, dict)
    assert "error" in result