import requests

good_code = '"""Module docstring."""\n\n\ndef add(a, b):\n    """Add two numbers."""\n    return a + b\n'

r = requests.post("http://localhost:5000/analyze", json={"code": good_code})
data = r.json()
print("Score:", data["score"])
print("Pylint score:", data["summary"]["pylint"]["score"])
print("Issues:", data["summary"]["pylint"]["issue_count"])