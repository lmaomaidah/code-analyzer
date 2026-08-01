"""
deployed_smoke_test.py
Owner: Maidah (Security & QA Lead)
Week:  Week 6 — post-deployment verification

Run this AFTER Maria deploys the backend to Render, pointed at the real
public URL, to confirm the deployed instance behaves the same way the
local test suite already proved it does.

This is a smoke test, not a substitute for the local pytest suite — it
can't inspect the deployed server's filesystem (Render's free tier gives
no shell access), so it verifies *behaviour* (correct status codes,
correct findings surfaced, no 500s) rather than disk state. See
SECURITY_AUDIT.md's Week 6 section for why that's still a reasonable
audit position.

Usage:
    python scripts/deployed_smoke_test.py https://your-app.onrender.com
"""

import sys
import json
import time
import requests


VULNERABLE_CODE = """
import hashlib

password = "super_secret_123"
hashed = hashlib.md5(password.encode()).hexdigest()
"""

CLEAN_CODE = '''"""Simple, documented module."""


def add(a: int, b: int) -> int:
    """Return the sum of a and b."""
    return a + b
'''

BLOCKED_CODE = "os.system('whoami')"


def check(label: str, condition: bool, detail: str = ""):
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {label}" + (f" — {detail}" if detail and not condition else ""))
    return condition


def main():
    if len(sys.argv) != 2:
        print("Usage: python deployed_smoke_test.py <deployed-base-url>")
        sys.exit(1)

    base_url = sys.argv[1].rstrip("/")
    all_passed = True

    # 1. Health check
    resp = requests.get(f"{base_url}/health", timeout=15)
    all_passed &= check(
        "GET /health returns 200",
        resp.status_code == 200,
        f"got {resp.status_code}",
    )

    # 2. Vulnerable code surfaces Bandit findings, never 500
    resp = requests.post(
        f"{base_url}/analyze", json={"code": VULNERABLE_CODE}, timeout=30
    )
    all_passed &= check(
        "Vulnerable code: status is 200 (not 500)",
        resp.status_code == 200,
        f"got {resp.status_code}",
    )
    if resp.status_code == 200:
        body = resp.json()
        bandit = body.get("summary", {}).get("bandit", {})
        all_passed &= check(
            "Vulnerable code: Bandit reports at least one finding",
            (bandit.get("high_count", 0) + bandit.get("medium_count", 0)) >= 1,
            json.dumps(bandit),
        )
        all_passed &= check(
            "Vulnerable code: score is present and numeric",
            isinstance(body.get("score"), (int, float)),
        )

    # 3. Clean code scores reasonably and has no HIGH findings
    resp = requests.post(f"{base_url}/analyze", json={"code": CLEAN_CODE}, timeout=30)
    all_passed &= check(
        "Clean code: status is 200",
        resp.status_code == 200,
        f"got {resp.status_code}",
    )
    if resp.status_code == 200:
        body = resp.json()
        all_passed &= check(
            "Clean code: no Bandit HIGH findings",
            body.get("summary", {}).get("bandit", {}).get("high_count", 1) == 0,
        )

    # 4. Blocked pattern rejected with 422, never 500
    resp = requests.post(f"{base_url}/analyze", json={"code": BLOCKED_CODE}, timeout=15)
    all_passed &= check(
        "Blocked pattern: status is 422 (not 500)",
        resp.status_code == 422,
        f"got {resp.status_code}",
    )

    # 5. Malformed / hostile inputs never 500 (repeat of test_edge_cases.py,
    #    run here against the real deployed instance)
    hostile_payloads = [
        {"code": ""},
        {"code": "x" * 50_001},
        {"github_url": "https://github.com/deleted-user-xyz/deleted-repo"},
        {},
    ]
    for payload in hostile_payloads:
        resp = requests.post(f"{base_url}/analyze", json=payload, timeout=15)
        all_passed &= check(
            f"Hostile payload never 500: {payload}",
            resp.status_code != 500,
            f"got {resp.status_code}",
        )
        time.sleep(0.5)  # be polite to the free-tier dyno

    print()
    print("ALL CHECKS PASSED" if all_passed else "ONE OR MORE CHECKS FAILED")
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()