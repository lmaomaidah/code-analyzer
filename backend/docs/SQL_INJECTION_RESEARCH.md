# SQL Injection Detection — Stretch Goal Research (Week 5)

Owner: Maidah (Security & QA Lead)
Status: Research only — **not implemented in the MVP**. This document
exists to inform a Week 7 go/no-go decision, not to describe a shipped
feature.

Companion doc: `backend/analyzers/SQL_INJECTION_RESEARCH.md` covers the
proposed module's architecture and contract (how it would plug into
`app.py` alongside Pylint/Radon/Bandit). This doc focuses on the security
content itself: the vulnerability patterns, what Bandit already catches,
and a concrete detection proposal.

---

## 1. The three most common SQL injection patterns in Python code

### Pattern A — Direct string concatenation into a query

**Vulnerable:**
```python
def get_user(conn, username):
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    return conn.execute(query)
```
If `username` is attacker-controlled (e.g. `' OR '1'='1`), the resulting
query's structure changes entirely — the classic injection.

**Safe (parameterised):**
```python
def get_user(conn, username):
    query = "SELECT * FROM users WHERE username = ?"
    return conn.execute(query, (username,))
```
The driver treats `username` as data, never as part of the SQL grammar,
regardless of its contents.

---

### Pattern B — Percent-formatting a variable into a query string

**Vulnerable:**
```python
def get_order(conn, order_id):
    query = "SELECT * FROM orders WHERE id = %s" % order_id
    return conn.execute(query)
```
This looks like it might be using the DB driver's placeholder syntax, but
`%` here is plain Python string formatting happening *before* the query
reaches the driver — the driver never gets a chance to escape anything.

**Safe (parameterised):**
```python
def get_order(conn, order_id):
    query = "SELECT * FROM orders WHERE id = %s"
    return conn.execute(query, (order_id,))
```
Passing the tuple as a second argument to `execute()` (rather than
pre-formatting the string) hands `order_id` to the driver as a bound
parameter instead of literal SQL text.

---

### Pattern C — f-string interpolation directly into a query

**Vulnerable:**
```python
def search_products(conn, term):
    query = f"SELECT * FROM products WHERE name LIKE '%{term}%'"
    return conn.execute(query)
```
f-strings make this pattern especially easy to write by accident — it
reads like ordinary string building, with no visual cue (like `%s` or
`?`) that anything is wrong.

**Safe (parameterised):**
```python
def search_products(conn, term):
    query = "SELECT * FROM products WHERE name LIKE ?"
    return conn.execute(query, (f"%{term}%",))
```
The wildcard `%` characters are safely built into the *value*; the query
*structure* stays a fixed string.

---

## 2. What Bandit already covers, and where the gap is

Bandit's **B608** (`hardcoded_sql_expressions`) already flags string-built
SQL near an `.execute()`-style call, and would catch Patterns A, B, and C
above in their simplest forms — string concatenation, `%`-formatting, and
f-string interpolation are all things B608's checker looks for textually
near query-execution calls.

**Where B608 has real gaps:**

1. **ORM-specific raw-SQL escape hatches.** Django's `QuerySet.raw()` and
   `.extra()`, and SQLAlchemy's `text()` with unescaped interpolation, sit
   outside the DB-API `cursor.execute()` shape B608 is tuned around. Code
   using these can build a string exactly like Pattern A/C above and
   Bandit may not flag it, because the call site doesn't look like a
   direct `execute()`.
2. **Query built in one function, executed in another.** B608 looks for
   string-building *near* an execute call in the same scope. If a
   function returns an unsafely-built query string and a *different*
   function executes it, there's no local textual proximity for B608 to
   key off. Catching this needs either simple intra-function data-flow
   tracking or an explicit heuristic accepting a higher false-positive
   rate.
3. **Confidence signalling.** Bandit reports a confidence level alongside
   severity for every finding. A dedicated module would need the same —
   presenting a heuristic match as a definitive finding would erode trust
   in the tool faster than just not shipping it.

---

## 3. Proposed detection approach (regex-based, explicitly a heuristic)

A minimal, honest starting point: flag any line where an f-string or
`%`/`.format()` string contains a SQL keyword (`SELECT`, `INSERT`,
`UPDATE`, `DELETE`) **and** interpolates a variable in the same
expression.

Conceptual pattern (illustrative, not final):
- Match f-strings / format-strings containing one of the four keywords
  above, case-insensitive.
- Within that match, check for at least one `{variable}` interpolation
  or `%` placeholder fed by a variable (not a literal).
- Flag the line with a `MEDIUM` confidence rating — deliberately not
  `HIGH`, because this is a textual heuristic, not AST-based data-flow
  analysis.

**Documented limitations, up front:**
- **False positives on safe code** — a query already using `?`/`%s`
  driver placeholders correctly can still contain a keyword +
  interpolated-looking text and get flagged if the regex isn't careful
  to exclude proper placeholder syntax.
- **Misses variable reassignment** — `query = base_query; query += extra`
  built across multiple lines defeats a single-line regex entirely.
- **No cross-function tracking** — Pattern-B-style "build here, execute
  there" gaps (see §2.2) would still be invisible to this approach unless
  it graduates to full AST parsing later, mirroring how Radon and Bandit
  themselves use `ast` rather than text matching specifically to avoid
  this whole class of false positive/false negative.

---

## 4. Recommendation

**Treat this as a genuine, but low-priority, Week 7 stretch goal.** The
research above shows Bandit's B608 already provides reasonable baseline
coverage for the two most common patterns (Patterns A and C), so a
dedicated module's marginal value is concentrated in the ORM-escape-hatch
gap (§2.1) — a real but narrower slice of risk than "SQL injection
detection" as a headline might suggest.

Building it properly (AST-based, confidence-rated, following the
scanner contract in `analyzers/SQL_INJECTION_RESEARCH.md`) is a
reasonable few-day effort. Building the *regex* version above is closer
to a few hours, but ships with meaningfully more false positives — for a
tool whose whole value proposition is a trustworthy quality score,
shipping a scanner that regularly cries wolf is worse than not shipping
one. **If Week 7 time is tight, skip it rather than ship the regex
version half-finished; if there's a spare day, the AST-based version is
worth doing properly.**