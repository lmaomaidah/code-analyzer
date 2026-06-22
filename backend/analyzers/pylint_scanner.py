"""
pylint_scanner.py
Owner: Maria (Backend Lead)
Week:  Skeleton in Week 1, full implementation in Week 3

Runs Pylint on submitted Python code and returns structured style/error findings.
"""

import subprocess
import json
import tempfile
import os


def run_pylint(code: str) -> dict:
    """
    Runs Pylint on the submitted code.

    Args:
        code (str): Raw Python source code as a string.

    Returns:
        dict: {
            "score":       float (Pylint's 0-10 score),
            "issues":      list of issue dicts,
            "issue_count": int,
            "error":       str or None
        }

    TODO (Week 3 — Maria):
        Step 1: Write code to a NamedTemporaryFile
        Step 2: Run subprocess: ["pylint", "--output-format=json", tmp_path]
        Step 3: Parse JSON output with _parse_pylint_output()
        Step 4: Delete temp file in a finally block
        Step 5: Return structured dict
    """
    # --- STUB ---
    return {
        "score":       0.0,
        "issues":      [],
        "issue_count": 0,
        "error":       None,
    }


def _parse_pylint_output(raw_json: list) -> dict:
    """
    Parses Pylint JSON output into our standard format.

    Pylint JSON structure (list of message objects):
        [
            {
                "type":    "convention" | "refactor" | "warning" | "error" | "fatal",
                "module":  "...",
                "obj":     "...",
                "line":    5,
                "column":  0,
                "message": "Missing module docstring",
                "message-id": "C0114",
                "symbol":  "missing-module-docstring"
            },
            ...
        ]

    Severity mapping:
        fatal / error  → HIGH
        warning        → MEDIUM
        convention / refactor → LOW

    TODO (Week 3 — Maria): implement this function.
    """
    severity_map = {
        "fatal":      "HIGH",
        "error":      "HIGH",
        "warning":    "MEDIUM",
        "convention": "LOW",
        "refactor":   "LOW",
    }

    issues = []
    # for item in raw_json:
    #     issues.append({
    #         "tool":       "pylint",
    #         "severity":   severity_map.get(item.get("type", ""), "LOW"),
    #         "message":    item.get("message"),
    #         "line":       item.get("line"),
    #         "symbol":     item.get("symbol"),
    #         "message_id": item.get("message-id"),
    #     })

    return {
        "score":       0.0,   # extract from pylint's final score line
        "issues":      issues,
        "issue_count": len(issues),
        "error":       None,
    }
