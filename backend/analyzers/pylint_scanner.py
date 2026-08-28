"""
pylint_scanner.py
Owner: Maria (Backend Lead)
Runs Pylint on submitted Python code and returns structured findings.

Week 5 fix (flagged by Maidah, root-caused via test_integration.py):
Score extraction previously did an exact substring match on
"Your code has been rated at". On at least one Windows/Python 3.13
environment, Pylint 3.2.5's text reporter wraps that line WITHOUT a
space between "rated" and "at" (observed output: "...has been ratedat
10.00/10..."), likely a terminal-width detection quirk when Pylint is
run as a subprocess with no real TTY attached. The exact-substring
match silently never fired in that case, so `score` stayed at its 0.0
default on every single request -- not a crash, just silently wrong
data feeding directly into compute_score(). Replaced with a regex that
tolerates zero-or-more whitespace around "at" (and negative scores,
which Pylint can produce for very bad code).
"""
import subprocess
import sys
import json
import re
import tempfile
import os

# Matches "rated at X.XX/10", "ratedat X.XX/10", "rated  at  X.XX / 10",
# case-insensitively, and captures the (possibly negative) score.
SCORE_PATTERN = re.compile(r"rated\s*at\s*(-?\d+\.?\d*)\s*/\s*10", re.IGNORECASE)


def run_pylint(code: str) -> dict:
    """
    Runs Pylint on the submitted code.
    Returns structured dict with score, issues, and issue count.
    """
    tmp_path = None
    try:
        # Step 1: Write code to a temp file
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8"
        ) as tmp:
            tmp.write(code)
            tmp_path = tmp.name

        # Step 2: Run Pylint for JSON issues
        json_result = subprocess.run(
            [sys.executable, "-m", "pylint", tmp_path, "--output-format=json"],
            capture_output=True,
            text=True
        )

        # Step 3: Run Pylint separately for score
        score_result = subprocess.run(
            [sys.executable, "-m", "pylint", tmp_path, "--output-format=text", "--score=yes"],
            capture_output=True,
            text=True
        )

        # Step 4: Parse JSON issues
        raw = json_result.stdout.strip()
        try:
            messages = json.loads(raw) if raw else []
        except json.JSONDecodeError:
            messages = []

        parsed = _parse_pylint_output(messages)

        # Step 5: Extract score from text output.
        # Regex-based (see module docstring) instead of an exact
        # substring match, specifically to survive the missing-space
        # line-wrap quirk seen on some Windows/Python 3.13 setups.
        score = 0.0
        all_text = score_result.stdout + score_result.stderr
        match = SCORE_PATTERN.search(all_text)
        if match:
            try:
                score = float(match.group(1))
            except ValueError:
                score = 0.0

        parsed["score"] = max(score, 0.0)
        return parsed

    except Exception as e:
        return {
            "score": 0.0,
            "issues": [],
            "issue_count": 0,
            "error": str(e)
        }

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


def _parse_pylint_output(raw_json: list) -> dict:
    """
    Parses Pylint JSON output into our standard format.
    """
    severity_map = {
        "fatal":      "HIGH",
        "error":      "HIGH",
        "warning":    "MEDIUM",
        "convention": "LOW",
        "refactor":   "LOW",
    }

    issues = []
    for item in raw_json:
        issues.append({
            "tool":       "pylint",
            "severity":   severity_map.get(item.get("type", ""), "LOW"),
            "message":    item.get("message"),
            "line":       item.get("line"),
            "symbol":     item.get("symbol"),
            "message_id": item.get("message-id"),
        })

    return {
        "score":       0.0,
        "issues":      issues,
        "issue_count": len(issues),
        "error":       None,
    }
