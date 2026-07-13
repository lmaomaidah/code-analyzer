"""
pylint_scanner.py
Owner: Maria (Backend Lead)
Runs Pylint on submitted Python code and returns structured findings.
"""
import subprocess
import json
import tempfile
import os

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

        # Step 2: Run Pylint on the temp file
        result = subprocess.run(
            ["pylint", tmp_path, "--output-format=json", "--score=yes"],
            capture_output=True,
            text=True
        )

        # Step 3: Parse the JSON output
        raw = result.stdout.strip()
        if not raw:
            return {
                "score": 10.0,
                "issues": [],
                "issue_count": 0,
                "error": None
            }

        try:
            messages = json.loads(raw)
        except json.JSONDecodeError:
            messages = []

        parsed = _parse_pylint_output(messages)

        # Step 4: Extract score from stderr
        score = 0.0
        for line in result.stderr.splitlines() + result.stdout.splitlines():
            if "Your code has been rated at" in line:
                try:
                    score = float(line.split("at")[1].split("/")[0].strip())
                except (ValueError, IndexError):
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
        # Step 5: Always delete temp file
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