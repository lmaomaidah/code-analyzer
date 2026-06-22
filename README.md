# Automated Code Quality Analyzer

A web-based tool that analyzes Python source code for quality issues, complexity metrics, and security vulnerabilities.

**Tech Stack:** Python · Flask · React · Vite · Pylint · Radon · Bandit

---

## Team

| Name   | Role              | Branch            |
|--------|-------------------|-------------------|
| Maria  | Backend Lead      | `backend/maria`   |
| Hira   | Frontend Lead     | `frontend/hira`   |
| Maidah | Security & QA     | `security/maidah` |

---

## Project Structure

```
code-quality-analyzer/
├── backend/               ← Flask API (Maria)
│   ├── app.py             ← Entry point
│   ├── requirements.txt
│   ├── analyzers/         ← One module per tool (Pylint / Radon / Bandit)
│   ├── utils/             ← Input validation helpers
│   └── tests/             ← Unit tests
└── frontend/              ← React + Vite (Hira)
    ├── index.html
    └── src/
        ├── App.jsx
        └── pages/
            └── InputPage.jsx
```

---

## Local Setup

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
# Runs at http://localhost:5000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# Runs at http://localhost:5173
```

---

## API

See [`backend/API.md`](backend/API.md) for full endpoint documentation.

---

## Branch Rules

- `main` is protected — no direct pushes
- Each person works on their own branch and opens a Pull Request to merge
- At least one other team member should review before merging
