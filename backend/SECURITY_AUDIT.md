# Security Audit — Week 2

Owner: Maidah (Security & QA Lead)
Scope: `backend/` (excluding `tests/`)
Tool: `bandit -r . -x ./tests -f json`

---

## Summary

| Severity | Count |
|----------|-------|
| HIGH     | 1     |
| MEDIUM   | 0     |
| LOW      | 2     |

One real, actionable finding. Two informational-only findings that don't
need a code change but are documented for completeness.

---

## Finding 1 — Flask debug mode hardcoded on (HIGH)

- **File:** `app.py`, line 80 (pre-fix)
- **Bandit ID:** B201 `flask_debug_true`
- **Issue:** `app.run(debug=True)` was hardcoded. Flask's debug mode enables
  the Werkzeug interactive debugger, which lets anyone who can trigger an
  unhandled exception in the running app execute arbitrary Python in the
  browser. Since `/analyze` runs external tools (Pylint/Radon/Bandit) on
  untrusted input, an unexpected crash is not far-fetched.
- **Status:** **Fixed.** `app.py` now reads debug mode from the
  `FLASK_DEBUG` environment variable (already defined in `.env.example`)
  and defaults to `off`. Debug mode is only on if someone explicitly sets
  `FLASK_DEBUG=1` locally.
- **Why this matters for Render deployment:** the free tier has no reason
  to ever run with debug on — this closes that off by default rather than
  relying on everyone remembering to change it before deploying.

---

## Finding 2 & 3 — `subprocess` import flagged (LOW / informational)

- **Files:** `analyzers/bandit_scanner.py` line 9, `analyzers/pylint_scanner.py` line 9
- **Bandit ID:** B404 `blacklist`
- **Issue:** Bandit flags any `import subprocess` as worth a second look,
  since subprocess calls are a common source of shell injection.
- **Assessment:** Not a real issue *yet* — both files are still Week 1
  stubs and don't call `subprocess.run`/`Popen` at all. This flag exists to
  remind us to review the actual call sites once Week 3 fills them in.
- **Status:** No fix needed now. Re-run this audit after Week 3's real
  `run_bandit()` / `run_pylint()` implementations land, and specifically
  check that:
  - the temp file path is never built from unsanitized input,
  - `shell=True` is never used (this is already one of our
    `BLOCKED_PATTERNS` for submitted code — worth double-checking our own
    subprocess calls follow the same rule),
  - argument lists are used instead of a single shell string.

---

## Manual bypass attempts against `validator.py`

Beyond running Bandit, I tried to hand-craft inputs that might slip past
`BLOCKED_PATTERNS` as it stood at the start of Week 2 (only
`__import__('os')` was blocked):

| Attempt                                         | Result before Week 2 | Result now |
|--------------------------------------------------|-----------------------|------------|
| `__import__('subprocess')`                       | ❌ passed (bypass)    | ✅ blocked |
| `exec(compile(..., 'exec'))`                     | ❌ passed (bypass)    | ✅ blocked |
| `eval(input())`                                  | ❌ passed (bypass)    | ✅ blocked |
| `os.system('whoami')`                            | ❌ passed (bypass)    | ✅ blocked |
| `subprocess.call(cmd, shell=True)`                | ❌ passed (bypass)    | ✅ blocked |
| `open('/tmp/x', 'w').write('data')`              | ❌ passed (bypass)    | ✅ blocked |

Each of these is now covered by `BLOCKED_PATTERNS` in `validator.py`
(6 patterns total, up from 1) and has a corresponding pair of tests in
`test_validator.py` — one confirming the malicious form is blocked, one
confirming a similar-looking *safe* form (e.g. `open(f, 'r')`,
`shell=False`, plain `os.getcwd()`) is still allowed through.

**Known limitation:** these are regex checks on the source text, not AST
analysis, so they can still be bypassed with enough obfuscation (e.g.
string concatenation to build `"ex" + "ec"`, or base64-encoded payloads
decoded and exec'd). Real protection ultimately comes from **never
executing submitted code ourselves** — Bandit/Pylint/Radon only ever
*parse* it. This layer exists to keep obviously hostile input from making
it to disk or into a subprocess call at all, not as the only line of
defence.

---

## GitHub URL reachability

Added a live `requests.head()` check in `_validate_github_url()`:

- Non-200 response (private repo, deleted repo, typo'd URL) → rejected
  with a clear message before it ever reaches `github_fetcher.py`.
- Network errors / timeouts → rejected with a distinct "could not
  connect" message rather than crashing the request.
- Tests mock `requests.head` so the suite doesn't depend on network
  access or on any specific repo staying public.

---

## Test suite status

All existing Week 1 tests plus the new Week 2 tests pass locally:

```
python -m pytest tests/ -v
```

---

## Week 3 update — Bandit scanner implementation

`bandit_scanner.py` is now fully implemented (temp file → subprocess →
JSON parse → cleanup). Key security decisions:

- **Temp file cleanup happens in a `finally` block**, so it runs even if
  Bandit times out, isn't installed, returns malformed JSON, or crashes.
  Verified by `test_temp_file_is_deleted_after_scan` and
  `test_temp_file_deleted_even_when_bandit_errors` in
  `test_bandit_scanner.py`.
- **No `shell=True` anywhere in our own subprocess call** — Bandit is
  invoked with a list of args (`["bandit", "-f", "json", "-q", tmp_path]`),
  so submitted code has no path to inject additional shell commands via
  the scanner invocation itself, even though the submitted code lives in
  a file Bandit then parses.
- **A timeout (15s)** on the Bandit subprocess call, so a pathological
  input can't hang a request indefinitely on the free-tier dyno.
- Re-ran `bandit -r . -x ./tests` after this change. Two new LOW/
  informational findings appeared, both expected and both assessed as safe:
  - **B603** `subprocess_without_shell_equals_true` — flagged because we
    call `subprocess.run()` without explicitly passing `shell=False`.
    We *never* set `shell=True` anywhere in this file, and the command is
    a fixed list (`["bandit", "-f", "json", "-q", tmp_path]`) with no
    string concatenation, so there's no injection surface — Bandit flags
    this pattern defensively regardless of whether shell is actually used.
  - **B607** `start_process_with_partial_path` — flagged because we invoke
    `"bandit"` by name rather than a full path like
    `/usr/local/bin/bandit`. Acceptable here since `bandit` comes from
    `requirements.txt` inside our own controlled virtualenv/container, not
    from an arbitrary or user-influenced `PATH`.
  - No code change needed for either; documenting the reasoning here so a
    future audit doesn't have to re-derive it.

## Week 4 update — end-to-end integration & persistence testing

Added `tests/test_security_integration.py`, which hits the real
`/analyze` endpoint via Flask's test client (rather than calling
`run_bandit()`/`validate_input()` directly) to confirm the whole request
path behaves correctly:

- Known-vulnerable code submitted via `/analyze` surfaces Bandit's finding
  in the actual JSON response (`summary.bandit`, `issues[]`).
- Confirmed the two security layers stack correctly: code containing
  `shell=True` never reaches Bandit at all — the validator's
  `BLOCKED_PATTERNS` rejects it first with a 422. (This is why the
  integration test's "vulnerable code" sample uses a weak-hash pattern
  instead of shell injection — see the comment in the test file.)
- Repeated the temp-file persistence check at the API level, including a
  version that simulates Bandit crashing mid-scan, to guard against a
  future change to `app.py` reintroducing a leak.
- **Known limitation:** the task list also asks to verify vulnerable code
  produces an "appropriately low" score. `compute_score()` in `app.py` is
  still the Week 4 placeholder (`return 75`) regardless of scanner
  findings — that formula is Maria's Week 4 deliverable, not yet done.
  The relevant test is written but commented out with a note explaining
  why, ready to enable once `compute_score()` is real.

## SQL injection stretch goal

Research-only notes for the deferred SQL injection detection module are in
`analyzers/SQL_INJECTION_RESEARCH.md`. Not implemented — intentionally
deferred until after the MVP is stable, per the locked sprint scope.
