# Security & QA — Final Report Section

Owner: Maidah (Security & QA Lead)
Scope: `backend/` security design, testing, and audit findings across the
full 7-week project.

---

## 1. Input validation design

All input to `/analyze` passes through `validate_input()` in
`utils/validator.py` before any scanner or the GitHub fetcher ever sees
it. Two independent input modes are supported — pasted code or a GitHub
URL — and the validator enforces mutual exclusivity, length bounds
(10–50,000 characters, chosen to keep Pylint+Radon+Bandit's combined
runtime within a few seconds on Render's free-tier CPU), and GitHub URL
shape.

`BLOCKED_PATTERNS` is a second, narrower layer specifically for
constructs that could turn "static analysis of submitted code" into
"execution of submitted code" — `exec()`, `eval()`, `os.system()`,
`shell=True`, `__import__('os'/'subprocess')`, and write-mode `open()`.
Each pattern was chosen because it represents a way submitted code could
affect the server itself, rather than just being analysed by it. Every
pattern has a paired test in `test_validator.py`: one confirming the
dangerous form is blocked, one confirming a similarly-shaped but safe
form (e.g. `open(f, 'r')`, `shell=False`) still passes — so the validator
doesn't quietly become overzealous over time.

**Known limitation, stated honestly:** these are regex checks on source
text, not AST analysis, so determined obfuscation (string concatenation
to build `"ex"+"ec"`, base64-encoded-then-decoded payloads) could
theoretically slip past them. This is why the deeper guarantee is
architectural, not pattern-matching: **submitted code is never executed
by this application, only parsed** by Pylint, Radon, and Bandit. The
blocked-pattern layer exists to keep obviously hostile input from
reaching disk or a subprocess call at all — a defence-in-depth measure,
not the only line of defence.

---

## 2. Bandit integration

`analyzers/bandit_scanner.py` writes submitted code to a temp file (Bandit
requires a real file path), invokes Bandit as a subprocess with an
explicit argument list (never `shell=True`, never a concatenated shell
string — the submitted code has no path to inject additional shell
commands via the scanner invocation itself), and parses the resulting
JSON into the same issue shape Pylint's output uses, so the dashboard can
render both tools' findings uniformly.

Temp-file cleanup happens in a `finally` block — verified by
`test_temp_file_is_deleted_after_scan` and
`test_temp_file_deleted_even_when_bandit_errors`, which explicitly
simulates a Bandit crash mid-scan and confirms the file is still removed.
This guarantee is re-verified at the full-request level in
`test_security_integration.py` and `test_integration.py`, which check the
real `/tmp` directory before and after a live `/analyze` call rather than
only unit-testing the scanner function in isolation.

---

## 3. Self-audit finding: Flask debug mode

Bandit's own self-scan of the backend (`bandit -r . -x ./tests`) caught
`app.run(debug=True)` hardcoded in `app.py` early in the project — a real
finding, not a false positive. Debug mode enables Werkzeug's interactive
debugger, which lets anyone able to trigger an unhandled exception in the
running app execute arbitrary Python from their browser. Since
`/analyze` deliberately runs external tools against untrusted input, an
unexpected crash was never a remote scenario.

**Fixed:** debug mode now reads from the `FLASK_DEBUG` environment
variable (already present in `.env.example`) and defaults to off, so
Render deployment is safe by default rather than depending on someone
remembering to flip a flag before shipping.

Two informational-only findings (B603/B607, both about how the Bandit
subprocess itself is invoked) were reviewed and assessed as safe — no
`shell=True` anywhere, fixed argument list, `bandit` resolved from the
project's own `requirements.txt` inside a controlled environment. Full
reasoning is in `SECURITY_AUDIT.md` so a future audit doesn't have to
re-derive it.

---

## 4. Temp-file handling guarantee

No code submitted through `/analyze` is ever written to disk except as a
short-lived temp file inside Bandit's and Pylint's own scan functions,
and both guarantee cleanup via `finally` blocks regardless of success,
timeout, or crash. This is tested at three levels: the scanner unit tests
(function-level), the integration tests (full HTTP request, real `/tmp`
inspection), and — for the deployed environment specifically — a
documented architectural argument rather than a remote filesystem check,
since Render's free tier provides no external shell access to verify a
live dyno's disk state directly (see `SECURITY_AUDIT.md`'s Week 6
section for the full reasoning, and
`scripts/deployed_smoke_test.py` for what *is* verifiable remotely:
correct behaviour against the live URL).

---

## 5. SQL injection research summary

A dedicated SQL injection scanner was explored as a stretch goal and is
**not implemented** — this was a deliberate scope decision, not a missed
deadline. Research (`docs/SQL_INJECTION_RESEARCH.md`) found that Bandit's
existing B608 check already covers the two most common vulnerable
patterns (string concatenation and f-string interpolation into SQL
queries); the real gap is narrower than "SQL injection detection" as a
headline suggests — mainly ORM-specific raw-SQL escape hatches (Django
`.raw()`/`.extra()`, SQLAlchemy `text()`). A regex-based detector was
designed as a possible starting point but explicitly **not recommended**
for this project: it would trade a narrow amount of extra coverage for a
meaningful false-positive rate, which undermines trust in a tool whose
entire value proposition is a *trustworthy* quality score. Recommendation
stands as documented: pick this up in Week 7 only if time allows, and
prefer the properly AST-based version over the regex shortcut if it is
picked up at all.

---

## 6. Test suite summary

| Area                          | File(s)                                             | What it proves |
|--------------------------------|------------------------------------------------------|-----------------|
| Input validation                | `test_validator.py`                                  | Every rule in `validation_rules.md`, plus paired blocked/safe cases for every `BLOCKED_PATTERNS` entry |
| Bandit scanner (unit)           | `test_bandit_scanner.py`                              | Correct findings, correct severity mapping, temp-file cleanup on success and on crash |
| GitHub fetching                 | `test_github_fetcher.py`                              | Real repo, fake repo, rate-limit handling, 50,000-char cap |
| Full-request security layering  | `test_security_integration.py`                        | Validator-then-Bandit stacking, persistence guarantee at the API level |
| Full-pipeline scoring            | `test_integration.py`                                 | Clean vs. messy/vulnerable code produce meaningfully different scores; response shape matches `API.md` |
| Crash resilience                | `test_edge_cases.py`                                   | Six documented boundary/hostile inputs, all fail cleanly, never a 500 |
| App-level endpoints              | `test_app.py`                                          | `/health`, `/analyze` happy paths and malformed-request handling |

All of the above run green together via `python -m pytest tests/ -v`
with no skipped tests (aside from the two GitHub-fetcher tests that
gracefully skip only if the GitHub API rate limit is actually hit at
test time).