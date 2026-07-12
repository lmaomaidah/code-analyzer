"""
validator.py
Owner: Maidah (Security & QA Lead)
Week:  Week 1 skeleton, Week 2 hardening

Validates and sanitizes all user input before it reaches the analysis engine.
This is the first line of defence against malformed or malicious input.
"""

import re
import requests

# ── Constants (mirrors validation_rules.md) ──────────────────────────────────

MAX_CODE_LENGTH   = 50_000       # characters
MIN_CODE_LENGTH   = 10           # characters — reject near-empty submissions
GITHUB_URL_PREFIX = "https://github.com/"
GITHUB_URL_REGEX  = re.compile(
    r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/?$"
)
GITHUB_TIMEOUT_SECONDS = 5

# Characters/constructs that could be used to manipulate the server
# filesystem, shell, or interpreter. Bandit/Pylint/Radon all run against
# this code (either as a subprocess on a temp file, or directly in-process
# for Radon), so we sanitize before any of it reaches those tools.
#
# Week 2 research notes (Maidah): started from the Bandit plugin index
# (https://bandit.readthedocs.io/en/latest/plugins/index.html) and picked
# the constructs that are dangerous the moment they're *present* in a
# string, regardless of whether the code actually runs (Radon parses code
# directly; a crafted docstring/comment could still be read by tooling
# that isn't as careful as Bandit is with AST-only parsing).
BLOCKED_PATTERNS = [
    # __import__('os') — imports a dangerous module via a string, bypassing
    # simple "import os" greps.
    re.compile(r"__import__\s*\(\s*['\"]os['\"]"),

    # __import__('subprocess') — same trick, targeting subprocess instead.
    re.compile(r"__import__\s*\(\s*['\"]subprocess['\"]"),

    # exec(...) — runs arbitrary code built from a string at runtime. There's
    # no legitimate reason for analyzer input to need this.
    re.compile(r"\bexec\s*\("),

    # eval(...) — same risk as exec(), commonly used to smuggle in dynamic
    # code that static analysis alone won't catch.
    re.compile(r"\beval\s*\("),

    # os.system(...) — direct shell command execution.
    re.compile(r"os\.system\s*\("),

    # shell=True — when paired with subprocess calls this enables full shell
    # command injection rather than a single controlled executable.
    re.compile(r"shell\s*=\s*True"),

    # open(..., 'w'/'a'/'x') — write/append/create file modes. Submitted code
    # is only ever supposed to be *read* and analysed, never used to write
    # files on the server's filesystem.
    re.compile(r"open\s*\([^)]*['\"][waxWAX][+tb]?['\"]"),
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

    # Week 2 (Maidah): live reachability check. A HEAD request is enough to
    # confirm the repo exists and is public — no need to download anything
    # here, Maria's github_fetcher.py does the real fetching later.
    # We deliberately fail *closed*: any network error, timeout, or non-200
    # response is treated as "not usable" rather than silently passing the
    # URL through to the fetcher.
    try:
        resp = requests.head(
            url, timeout=GITHUB_TIMEOUT_SECONDS, allow_redirects=True
        )
        if resp.status_code != 200:
            return False, "GitHub repository is not reachable or is private."
    except requests.RequestException:
        return False, "Could not connect to GitHub. Check the URL and try again."

    return True, ""
