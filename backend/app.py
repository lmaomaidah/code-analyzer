from flask import Flask, request, jsonify
from flask_cors import CORS

from analyzers.pylint_scanner import run_pylint
from analyzers.radon_scanner import run_radon
from analyzers.bandit_scanner import run_bandit
from utils.validator import validate_input

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
    """
    Combines scanner results into a single quality score (0-100).

    TODO (Week 4): implement real weighted formula.
    Formula will be documented in API.md once finalised.
    """
    return 75  # placeholder


if __name__ == "__main__":
    app.run(debug=True)
