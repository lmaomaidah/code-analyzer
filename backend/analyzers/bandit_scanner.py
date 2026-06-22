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

    TODO (Week 3 — Maidah):
        Step 1: Write code to a NamedTemporaryFile (delete=False so Bandit can read it)
        Step 2: Run subprocess: ["bandit", "-f", "json", "-q", tmp_path]
        Step 3: Parse the JSON output with _parse_bandit_output()
        Step 4: Delete the temp file in a finally block (NEVER leave user code on disk)
        Step 5: Return the structured dict
    """
    # --- STUB — returns empty results until Week 3 ---
    return {
        "issues":       [],
        "high_count":   0,
        "medium_count": 0,
        "low_count":    0,
        "error":        None,
    }


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

    TODO (Week 3 — Maidah): implement this function.
    """
    issues = []
    counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}

    # for item in raw_json.get("results", []):
    #     severity = item.get("issue_severity", "LOW")
    #     counts[severity] += 1
    #     issues.append({
    #         "tool":       "bandit",
    #         "severity":   severity,
    #         "confidence": item.get("issue_confidence"),
    #         "message":    item.get("issue_text"),
    #         "line":       item.get("line_number"),
    #         "test_id":    item.get("test_id"),
    #     })

    return {
        "issues":       issues,
        "high_count":   counts["HIGH"],
        "medium_count": counts["MEDIUM"],
        "low_count":    counts["LOW"],
        "error":        None,
    }
