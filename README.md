# Dummy ID Generator

Icebolethu Group tool for generating valid-format South African ID numbers
(with matching member and next-of-kin details) for system testing.

**For testing only — never use these numbers for real identity verification.**

## Run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py            # http://127.0.0.1:8000
FLASK_DEBUG=1 python app.py   # with auto-reload / debugger
```

## Production

```bash
gunicorn app:app
```
