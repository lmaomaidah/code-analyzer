# Backend API Reference

Base URL (local): `http://localhost:5000`  
Base URL (deployed): `https://your-render-url.onrender.com` ← update when deployed

---

## GET /health

Confirms the server is running.

**Response**
```json
{ "status": "ok" }
```

---

## POST /analyze

Runs all three scanners on submitted Python code and returns a quality report.

### Request Body (JSON)

Option A — paste code directly:
```json
{
  "code": "import os\nprint(os.getcwd())"
}
```

Option B — GitHub URL (Week 2):
```json
{
  "github_url": "https://github.com/username/repo"
}
```

### Validation Rules

| Field        | Rule                                                     |
|--------------|----------------------------------------------------------|
| `code`       | Required if no `github_url`. Max 50,000 characters.     |
| `github_url` | Must start with `https://github.com/`. Repo must be public. |
| Both empty   | Returns 422 error.                                       |

### Success Response (200)

```json
{
  "score": 72,
  "issues": [
    {
      "tool":     "bandit",
      "severity": "HIGH",
      "message":  "Use of subprocess with shell=True",
      "line":     14
    },
    {
      "tool":     "pylint",
      "severity": "MEDIUM",
      "message":  "Missing module docstring",
      "line":     1
    }
  ],
  "summary": {
    "pylint": {
      "score":      6.5,
      "issues":     [...],
      "issue_count": 4
    },
    "radon": {
      "average_complexity": 3.2,
      "maintainability_index": 68.4,
      "functions": [...]
    },
    "bandit": {
      "issues":      [...],
      "high_count":  1,
      "medium_count": 2,
      "low_count":   0
    }
  }
}
```

### Error Responses

| Status | Meaning                        |
|--------|--------------------------------|
| 400    | No JSON body provided          |
| 422    | Input failed validation        |
| 500    | Internal server / scanner error |

---

## Score Formula (Week 4 — TBD)

The `score` field is calculated as a weighted combination:

| Component              | Weight | Notes                        |
|------------------------|--------|------------------------------|
| Pylint score (0-10)    | 40%    | Normalised to 0-100          |
| Radon complexity       | 30%    | Lower complexity = higher score |
| Bandit severity count  | 30%    | HIGH issues penalised heavily |

> Formula is a placeholder until Week 4. Weights may be adjusted after testing.
