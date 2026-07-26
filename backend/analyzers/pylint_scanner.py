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

        # Step 2: Run Pylint for JSON issues
        json_result = subprocess.run(
            ["pylint", tmp_path, "--output-format=json"],
            capture_output=True,
            text=True
        )

        # Step 3: Run Pylint separately for score
        score_result = subprocess.run(
            ["pylint", tmp_path, "--output-format=text", "--score=yes"],
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

        # Step 5: Extract score from text output
        score = 0.0
        all_text = score_result.stdout + score_result.stderr
        for line in all_text.splitlines():
            if "Your code has been rated at" in line:
                try:
                    rated_part = line.split("rated at")[1].strip()
                    score_str = rated_part.split("/")[0].strip()
                    score = float(score_str)
                    break
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