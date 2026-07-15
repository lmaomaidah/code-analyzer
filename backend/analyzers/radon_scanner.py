"""
radon_scanner.py
Owner: Maria (Backend Lead)
Runs Radon on submitted Python code to measure complexity.
"""
from radon.complexity import cc_visit
from radon.metrics import mi_visit

def run_radon(code: str) -> dict:
    """
    Runs Radon complexity and maintainability analysis.
    Returns structured dict with complexity scores.
    """
    try:
        blocks = cc_visit(code)
        parsed = _parse_complexity(blocks)

        try:
            mi_score = mi_visit(code, multi=True)
            maintainability = round(mi_score, 2)
        except Exception:
            maintainability = 0.0

        return {
            "average_complexity":    parsed["average_complexity"],
            "maintainability_index": maintainability,
            "functions":             parsed["functions"],
            "error":                 None,
        }

    except Exception as e:
        return {
            "average_complexity":    0.0,
            "maintainability_index": 0.0,
            "functions":             [],
            "error":                 str(e),
        }


def _parse_complexity(blocks: list) -> dict:
    """
    Converts Radon cc_visit() output into standard format.
    """
    functions = []
    total = 0

    for block in blocks:
        total += block.complexity
        functions.append({
            "name":       block.name,
            "complexity": block.complexity,
            "rank":       getattr(block, "rank", "A"),
            "line":       block.lineno,
        })

    average = round(total / len(functions), 2) if functions else 0.0

    return {
        "average_complexity": average,
        "functions":          functions,
    }