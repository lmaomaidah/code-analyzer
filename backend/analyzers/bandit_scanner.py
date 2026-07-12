"""
bandit_scanner.py
Owner: Maidah (Security & QA Lead)
Week:  Skeleton in Week 1, full implementation in Week 3

Runs Bandit on submitted Python code and returns structured security findings.
"""

import subprocess
import json
import tempfile
import os

# Bandit's own severity/confidence values, kept as constants so a typo
# doesn't silently create a 4th bucket that never gets counted.
SEVERITY_LEVELS = ("HIGH", "MEDIUM", "LOW")

# Bandit exit codes: 0 = no issues found, 1 = issues found (NOT a failure of
# the tool itself — that's the whole point of running it). Only treat other
# exit codes as "Bandit itself broke".
BANDIT_OK_EXIT_CODES = (0, 1)

# Safety cap so a pathological input (or a Bandit hang) can't tie up the
# free-tier dyno indefinitely.
BANDIT_TIMEOUT_SECONDS = 15


def run_bandit(code: str) -> dict:
    """
    Runs Bandit static security analysis on the submitted code.

    Args:
        code (str): Raw Python source code as a string.

    Returns:
        dict: {
            "issues":       list of issue dicts (see _parse_bandit_output),
            "high_count":   int,
            "medium_count": int,
            "low_count":    int,
            "error":        str or None   ← set if Bandit itself failed
        }

    Security notes:
        - The temp file is created with delete=False (Bandit needs a real
          path to open), but it is ALWAYS removed in the `finally` block —
          even if Bandit crashes, times out, or returns malformed JSON.
          No user-submitted code is ever left on disk after this returns.
        - We never use shell=True and never build a shell command string —
          the subprocess call takes a list of args, so there's no way for
          submitted code to inject additional shell commands via the
          Bandit invocation itself (the code lives inside the temp file,
          not on the command line).
    """
    tmp_path = None

    try:
        # Step 1: write the submitted code to a temp file so Bandit (a CLI
        # tool) has a real file to analyse. NamedTemporaryFile with
        # delete=False so it stays on disk between this write and the
        # subprocess call below (Windows in particular can't have two
        # processes holding the same open temp file otherwise).
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as tmp_file:
            tmp_file.write(code)
            tmp_path = tmp_file.name

        # Step 2: run Bandit against that file only, as a JSON report.
        # -f json  → machine-readable output
        # -q       → quiet (suppress Bandit's own banner/progress noise)
        result = subprocess.run(
            ["bandit", "-f", "json", "-q", tmp_path],
            capture_output=True,
            text=True,
            timeout=BANDIT_TIMEOUT_SECONDS,
        )

        if result.returncode not in BANDIT_OK_EXIT_CODES:
            return {
                "issues":       [],
                "high_count":   0,
                "medium_count": 0,
                "low_count":    0,
                "error":        f"Bandit exited with code {result.returncode}: "
                                f"{result.stderr.strip()[:500]}",
            }

        # Step 3: parse Bandit's JSON output.
        try:
            raw_json = json.loads(result.stdout)
        except json.JSONDecodeError:
            return {
                "issues":       [],
                "high_count":   0,
                "medium_count": 0,
                "low_count":    0,
                "error":        "Could not parse Bandit output.",
            }

        return _parse_bandit_output(raw_json)

    except subprocess.TimeoutExpired:
        return {
            "issues":       [],
            "high_count":   0,
            "medium_count": 0,
            "low_count":    0,
            "error":        f"Bandit scan timed out after {BANDIT_TIMEOUT_SECONDS}s.",
        }

    except FileNotFoundError:
        # Bandit isn't installed / not on PATH in this environment.
        return {
            "issues":       [],
            "high_count":   0,
            "medium_count": 0,
            "low_count":    0,
            "error":        "Bandit is not installed or not on PATH.",
        }

    finally:
        # Step 4: ALWAYS delete the temp file, no matter what happened
        # above. This is the single most important line in this file from
        # a security standpoint — submitted code must never persist.
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


def _parse_bandit_output(raw_json: dict) -> dict:
    """
    Parses the raw JSON dict returned by `bandit -f json` into our standard format.

    Bandit JSON structure (relevant fields):
        raw_json["results"] = [
            {
                "issue_severity": "HIGH" | "MEDIUM" | "LOW",
                "issue_confidence": "HIGH" | "MEDIUM" | "LOW",
                "issue_text": "...",
                "line_number": 14,
                "filename": "...",
                "test_id": "B602",
                "test_name": "subprocess_popen_with_shell_equals_true"
            },
            ...
        ]
    """
    issues = []
    counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}

    for item in raw_json.get("results", []):
        severity = item.get("issue_severity", "LOW")
        if severity not in counts:
            severity = "LOW"  # defensive default if Bandit ever adds a level
        counts[severity] += 1

        issues.append({
            "tool":       "bandit",
            "severity":   severity,
            "confidence": item.get("issue_confidence"),
            "message":    item.get("issue_text"),
            "line":       item.get("line_number"),
            "test_id":    item.get("test_id"),
        })

    return {
        "issues":       issues,
        "high_count":   counts["HIGH"],
        "medium_count": counts["MEDIUM"],
        "low_count":    counts["LOW"],
        "error":        None,
    }
