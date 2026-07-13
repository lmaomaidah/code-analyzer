import pytest
from app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c

# ─── Test 1: Health check ────────────────────────────────────
def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.get_json()["status"] == "ok"

# ─── Test 2: Analyze with pasted code ────────────────────────
def test_analyze_with_code(client):
    r = client.post("/analyze", json={"code": "print('hello world')"})
    assert r.status_code == 200
    data = r.get_json()
    assert "score" in data
    assert "issues" in data
    assert "summary" in data

# ─── Test 3: Analyze with empty body ─────────────────────────
def test_analyze_empty_body(client):
    r = client.post("/analyze", json={})
    assert r.status_code == 400

# ─── Test 4: Analyze with no JSON ────────────────────────────
def test_analyze_no_json(client):
    r = client.post("/analyze")
    assert r.status_code == 415

# ─── Test 5: Analyze with fake GitHub URL ────────────────────
def test_analyze_fake_github_url(client):
    r = client.post("/analyze", json={"github_url": "https://github.com/fake99999/repo99999"})
    assert r.status_code == 422
    assert "error" in r.get_json()