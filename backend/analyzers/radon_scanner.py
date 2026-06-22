"""
radon_scanner.py
Owner: Maria (Backend Lead)
Week:  Skeleton in Week 1, full implementation in Week 3

Runs Radon on submitted Python code to measure cyclomatic complexity
and maintainability index.
"""

from radon.complexity import cc_visit, cc_rank
from radon.metrics import mi_visit


def run_radon(code: str) -> dict:
    """
    Runs Radon complexity and maintainability analysis on the submitted code.

    Args:
        code (str): Raw Python source code as a string.

    Returns:
        dict: {
            "average_complexity":    float,
            "maintainability_index": float  (0-100, higher = more maintainable),
            "functions":             list of per-function complexity dicts,
            "error":                 str or None
        }

    NOTE: Radon works directly on the code string — no temp file needed.

    TODO (Week 3 — Maria):
        Step 1: Call cc_visit(code) to get per-function complexity
        Step 2: Call mi_visit(code, multi=True) to get maintainability index
        Step 3: Build and return the structured dict below
    """
    # --- STUB ---
    return {
        "average_complexity":    0.0,
        "maintainability_index": 0.0,
        "functions":             [],
        "error":                 None,
    }


def _parse_complexity(blocks: list) -> dict:
    """
    Converts Radon's cc_visit() output into our standard format.

    Radon cc_visit() returns a list of Block objects with attributes:
        .name        — function/class name
        .complexity  — cyclomatic complexity (int)
        .rank        — 'A' (1-5) through 'F' (26+)
        .lineno      — line number
        .col_offset  — column

    Complexity rank guide:
        A (1-5)   → low risk, simple
        B (6-10)  → moderate
        C (11-15) → more complex
        D (16-20) → complex
        E (21-25) → highly complex
        F (26+)   → untestable

    TODO (Week 3 — Maria): implement this function.
    """
    functions = []
    total = 0

    # for block in blocks:
    #     total += block.complexity
    #     functions.append({
    #         "name":       block.name,
    #         "complexity": block.complexity,
    #         "rank":       block.rank,
    #         "line":       block.lineno,
    #     })

    average = total / len(functions) if functions else 0.0

    return {
        "average_complexity": round(average, 2),
        "functions":          functions,
    }
