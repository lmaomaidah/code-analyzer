# SQL Injection Detection — Stretch Goal Research

Owner: Maidah (Security & QA Lead)
Status: Research only (Week 4) — **not implemented**. This is explicitly a
post-MVP stretch goal; do not start building against this doc until the
core MVP (Weeks 1-4) is stable and the team has agreed to pick it up.

---

## Goal

A dedicated scanner module (`analyzers/sql_injection_scanner.py`, following
the same pattern as `bandit_scanner.py` / `radon_scanner.py`) that flags
Python code patterns commonly associated with SQL injection vulnerabilities,
as a supplement to Bandit's existing coverage.

## What Bandit already covers

Bandit already has relevant checks, so this module should **not duplicate**
them — it should fill gaps:

- **B608** `hardcoded_sql_expressions` — flags string-built SQL queries
  (e.g. f-strings or `%`/`.format()` concatenation feeding into `.execute()`).

This is a reasonable baseline, but it's a single regex-ish check on string
construction near `execute(...)` calls and can miss some real patterns.

## Gaps a dedicated module could fill

1. **ORM-adjacent raw query methods** — Django's `.raw()` and `.extra()`,
   SQLAlchemy's `text()` with unescaped interpolation, `cursor.executemany()`
   with string-built queries. Bandit's B608 is tuned around `sqlite3`/DB-API
   style calls and doesn't always catch ORM-specific raw-SQL escape hatches.
2. **String formatting adjacent to SQL keywords without an execute() call in
   the same function** — e.g. building a query string in one function and
   passing it to another. This needs either simple data-flow tracking within
   a function or an explicit acknowledgment that it's a heuristic with a
   higher false-positive rate.
3. **f-strings interpolating request-shaped variable names** — a heuristic
   check for f-strings containing SQL keywords (`SELECT`, `INSERT`, `DELETE`,
   `WHERE`) where the interpolated variable name suggests user input
   (`request`, `user_input`, `params`, etc). Explicitly a heuristic, would
   need a confidence rating like Bandit's, and should be documented as such
   rather than presented as a definitive finding.

## Suggested approach (if/when this is picked up)

- Keep it AST-based (via Python's built-in `ast` module) rather than regex,
  to reduce false positives compared to a purely textual check — this is
  the same reason Radon and Bandit both parse the AST instead of grepping.
- Follow the existing scanner contract so it plugs into `app.py` the same
  way Bandit/Pylint/Radon do:
  ```python
  def run_sql_injection_scan(code: str) -> dict:
      return {
          "issues": [...],       # same shape as bandit's issue dicts
          "high_count": int,
          "medium_count": int,
          "low_count": int,
          "error": str | None,
      }
  ```
- Reuse `bandit_scanner.py`'s temp-file pattern (write → scan → delete in
  `finally`) if the implementation ends up needing a real file rather than
  working on the `code` string directly via `ast.parse()`.
- Each finding should cite line number + a short reason, same as Bandit's
  `issue_text`, so it can slot into the same `issues` list the dashboard
  already renders.

## Explicitly out of scope for the stretch goal

- Detecting SQL injection in languages other than Python (the whole tool is
  Python-only for MVP).
- Detecting injection in raw SQL files uploaded separately — only code
  submitted through the existing `/analyze` flow.
- NoSQL injection patterns (Mongo, etc) — different vulnerability class,
  would be its own separate stretch goal if ever prioritized.

## Why this stays a stretch goal

Given the 7-week timeline and that the MVP scanners (Pylint/Radon/Bandit)
aren't fully wired end-to-end yet, adding a 4th scanner now risks scope
creep exactly as the sprint plan is trying to avoid. This doc exists so the
research isn't lost, not as a signal to start building.
