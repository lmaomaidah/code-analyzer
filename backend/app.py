import os

from flask import Flask, request, jsonify
from flask_cors import CORS

from analyzers.pylint_scanner import run_pylint
from analyzers.radon_scanner import run_radon
from analyzers.bandit_scanner import run_bandit
from utils.validator import validate_input
from utils.github_fetcher import fetch_github_code

app = Flask(__name__)
CORS(app)


@app.route("/health", methods=["GET"])
def health():
    """Simple health check — confirms the server is up."""
    return jsonify({"status": "ok"})


@app.route("/analyze", methods=["POST"])
def analyze():
    """
    Main analysis endpoint.

    Accepts JSON body:
        { "code": "<python source code string>" }
        OR
        { "github_url": "https://github.com/user/repo" }

    Returns JSON:
        {
          "score": <int 0-100>,
          "issues": [ { "tool", "severity", "message", "line" }, ... ],
          "summary": { "pylint": {...}, "radon": {...}, "bandit": {...} }
        }

    TODO (Week 3-4): wire up the real scanner modules below.
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "No JSON body provided"}), 400

    # --- Validate input (Maidah's validator) ---
    is_valid, error_msg = validate_input(data)
    if not is_valid:
        return jsonify({"error": error_msg}), 422

  # Handle both input modes — pasted code OR GitHub URL
    
        # Handle both input modes — pasted code OR GitHub URL
    if "github_url" in data:
        try:
            code = fetch_github_code(data["github_url"])
        except ValueError as e:
            return jsonify({"error": str(e)}), 422
    else:
        code = data.get("code", "")

    # --- Run scanners (Week 3: replace stubs with real calls) ---
    pylint_result = run_pylint(code)   # Maria — Week 3
    radon_result  = run_radon(code)    # Maria — Week 3
    bandit_result = run_bandit(code)   # Maidah — Week 3

    # --- Score calculation (Week 4) ---
    score = compute_score(pylint_result, radon_result, bandit_result)

    return jsonify({
        "score":   score,
        "issues":  pylint_result["issues"] + bandit_result["issues"],
        "summary": {
            "pylint": pylint_result,
            "radon":  radon_result,
            "bandit": bandit_result,
        }
    })

def compute_score(pylint_result, radon_result, bandit_result):
    """Weighted formula: Pylint 40% + Radon 30% + Bandit 30%"""

    # Pylint: score 0-10 → convert to 0-40
    pylint_raw = pylint_result.get("score", 0.0)
    pylint_score = (pylint_raw / 10.0) * 40

    # Radon: maintainability index 0-100 → convert to 0-30
    mi = radon_result.get("maintainability_index", 0.0)
    radon_score = (mi / 100.0) * 30

    # Bandit: start at 30, penalize for findings
    high   = bandit_result.get("high_count",   0)
    medium = bandit_result.get("medium_count", 0)
    bandit_score = max(0, 30 - (high * 10) - (medium * 5))

    # Final weighted score
    final = pylint_score + radon_score + bandit_score
    final = round(min(max(final, 0), 100), 1)

    return final


if __name__ == "__main__":
    # Security fix (Maidah, Week 2 audit — Bandit B201 flask_debug_true):
    # hardcoded debug=True exposes the Werkzeug interactive debugger, which
    # allows arbitrary code execution if the /analyze endpoint (or anything
    # else) ever throws an unhandled exception in production. Debug mode is
    # now opt-in via FLASK_DEBUG (see .env.example) and defaults to off.
    debug_mode = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug_mode)
