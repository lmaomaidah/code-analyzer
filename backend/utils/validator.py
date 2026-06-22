"""
validator.py
Owner: Maidah (Security & QA Lead)
Week:  Week 1

Validates and sanitizes all user input before it reaches the analysis engine.
This is the first line of defence against malformed or malicious input.
"""

import re

# ── Constants (mirrors validation_rules.md) ──────────────────────────────────

MAX_CODE_LENGTH   = 50_000       # characters
MIN_CODE_LENGTH   = 10           # characters — reject near-empty submissions
GITHUB_URL_PREFIX = "https://github.com/"
GITHUB_URL_REGEX  = re.compile(
    r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/?$"
)

# Characters that could be used to manipulate the server filesystem or shell.
# Bandit/Pylint run in subprocesses, so we sanitize before passing code along.
BLOCKED_PATTERNS = [
    # Shell escape attempts in code strings
    re.compile(r"__import__\s*\(\s*['\"]os['\"]"),   # __import__('os')
]


# ── Main entry point ─────────────────────────────────────────────────────────

def validate_input(data: dict) -> tuple[bool, str]:
    """
    Validates the JSON body from the /analyze endpoint.

    Args:
        data (dict): Parsed JSON body from the request.

    Returns:
        (True, "")           if input is valid
        (False, error_msg)   if input is invalid, with a human-readable reason

    Rules are documented in validation_rules.md
    """
    code       = data.get("code")
    github_url = data.get("github_url")

    # Must provide at least one input method
    if not code and not github_url:
        return False, "Provide either 'code' or 'github_url' in the request body."

    # Cannot provide both at once
    if code and github_url:
        return False, "Provide either 'code' or 'github_url', not both."

    if code is not None:
        return _validate_code(code)

    if github_url is not None:
        return _validate_github_url(github_url)

    return False, "Unknown validation error."


# ── Private helpers ───────────────────────────────────────────────────────────

def _validate_code(code: str) -> tuple[bool, str]:
    """Validates a raw code string submission."""

    if not isinstance(code, str):
        return False, "'code' must be a string."

    if len(code) < MIN_CODE_LENGTH:
        return False, f"Code is too short (minimum {MIN_CODE_LENGTH} characters)."

    if len(code) > MAX_CODE_LENGTH:
        return False, (
            f"Code exceeds maximum allowed length of {MAX_CODE_LENGTH} characters. "
            "Please submit a smaller file or use a GitHub URL."
        )

    # TODO (Maidah — Week 1/2): expand BLOCKED_PATTERNS based on
    # research into what could be used to attack the server itself.
    for pattern in BLOCKED_PATTERNS:
        if pattern.search(code):
            return False, "Submission contains a blocked pattern."

    return True, ""


def _validate_github_url(url: str) -> tuple[bool, str]:
    """Validates a GitHub repository URL."""

    if not isinstance(url, str):
        return False, "'github_url' must be a string."

    url = url.strip()

    if not url.startswith(GITHUB_URL_PREFIX):
        return False, f"GitHub URL must start with '{GITHUB_URL_PREFIX}'."

    if not GITHUB_URL_REGEX.match(url):
        return False, (
            "GitHub URL format is invalid. "
            "Expected: https://github.com/username/repository"
        )

    # TODO (Week 2 — Maria + Maidah): add a live reachability check here.
    # Use requests.head(url) and reject if status != 200.
    # This prevents 404 repos from reaching the analysis engine.

    return True, ""
