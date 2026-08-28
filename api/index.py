"""Vercel serverless entrypoint — serves the Flask app under /api/*.

Vercel rewrites route by the *destination* path, so /api/analyze would reach
this function as /api/index and lose the route. vercel.json passes the real
path in the __p query param instead; this shim restores it as PATH_INFO so
backend/app.py needs no Vercel-specific route changes.
"""
import os
import sys
from urllib.parse import parse_qs, urlencode

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app import app as flask_app  # noqa: E402


def app(environ, start_response):
    qs = parse_qs(environ.get("QUERY_STRING", ""), keep_blank_values=True)
    path = qs.pop("__p", [None])[0]
    if path is not None:
        environ["PATH_INFO"] = "/" + path
        environ["QUERY_STRING"] = urlencode(qs, doseq=True)
    elif environ.get("PATH_INFO", "").startswith("/api"):
        environ["PATH_INFO"] = environ["PATH_INFO"][4:] or "/"
    return flask_app(environ, start_response)
