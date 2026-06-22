# Input Validation Rules

Owner: Maidah (Security & QA Lead)
Status: Week 1 draft — review with team before Week 2

---

## Why Validation Matters Here

This tool runs external programs (Pylint, Radon, Bandit) on user-submitted code.
A poorly validated input could:
- Crash the server (oversized file, malformed encoding)
- Cause excessive resource usage (complex code that takes minutes to analyse)
- Potentially manipulate how the code gets written to a temp file

This doc defines exactly what "valid input" means so the validator.py implementation
and the test suite are working from the same source of truth.

---

## Rule Table

| Field          | Rule                                                                            | Error Message                                                     |
|----------------|---------------------------------------------------------------------------------|-------------------------------------------------------------------|
| Body (general) | Must be valid JSON with Content-Type: application/json                          | "No JSON body provided"                                           |
| Both fields    | Cannot send both `code` and `github_url` at once                                | "Provide either 'code' or 'github_url', not both."               |
| Neither field  | Must send at least one of `code` or `github_url`                                | "Provide either 'code' or 'github_url' in the request body."     |
| `code`         | Must be a string                                                                | "'code' must be a string."                                        |
| `code`         | Minimum 10 characters                                                           | "Code is too short (minimum 10 characters)."                      |
| `code`         | Maximum 50,000 characters                                                       | "Code exceeds maximum allowed length of 50,000 characters."       |
| `github_url`   | Must be a string                                                                | "'github_url' must be a string."                                  |
| `github_url`   | Must start with `https://github.com/`                                           | "GitHub URL must start with 'https://github.com/'."               |
| `github_url`   | Must match pattern: `https://github.com/<user>/<repo>` (no trailing paths)     | "GitHub URL format is invalid."                                   |
| `github_url`   | Repo must be publicly reachable (Week 2 check)                                  | "GitHub repository is not reachable or is private."               |

---

## Why 50,000 Characters?

Free-tier hosting (Render) has limited CPU and memory. Pylint + Radon + Bandit running
on a 50,000-character file takes approximately 5-10 seconds — acceptable for a free server.
A 500,000-character file could cause a timeout or crash the dyno.

If we want to support larger repos in the future, the right fix is to analyse only the
top-level files (not the whole repo) or to queue the job asynchronously.

---

## Blocked Patterns (Security)

These patterns in submitted code don't affect analysis correctness but could indicate
an attempt to abuse the temp-file write step. The validator rejects them before
the code reaches the filesystem.

| Pattern                        | Reason                                          |
|--------------------------------|-------------------------------------------------|
| `__import__('os')`             | Attempts to import OS module via string eval    |

TODO (Maidah, Week 1-2): Research additional patterns based on known
Python sandbox-escape techniques and add them to BLOCKED_PATTERNS in validator.py.
Good starting point: https://bandit.readthedocs.io/en/latest/plugins/index.html

---

## What We Do NOT Validate (Out of Scope for MVP)

- Whether the submitted code is syntactically valid Python (Pylint handles this gracefully)
- File encoding (we assume UTF-8 from the JSON body)
- Whether the code is actually Python vs another language (Pylint will produce errors but not crash)
