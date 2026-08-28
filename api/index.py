"""Vercel serverless entrypoint — serves the Flask app under /api/*.

Vercel routes /api/analyze here with PATH_INFO still set to "/api/analyze",
but Flask registers its routes as "/analyze". The shim strips the prefix so
backend/app.py needs no Vercel-specific route changes.
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from app import app as flask_app  # noqa: E402


def app(environ, start_response):
    path = environ.get("PATH_INFO", "")
    if path.startswith("/api"):
        environ["PATH_INFO"] = path[4:] or "/"
    return flask_app(environ, start_response)
