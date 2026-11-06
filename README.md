# ActaCite

ActaCite turns official college and office notices into evidence-linked task checklists. Every extracted action carries an exact source quote and page number, and uncertain or missing details are flagged for human review instead of guessed.

## Stack and data flow

The interface and application logic use Python and Streamlit. PyMuPDF reads PDFs; Tesseract is used as a fallback for scanned pages when installed. Candidate dates, actions, eligibility and document cues are extracted with date parsing and spaCy/NLP rules, then retained with their exact source quote and page. Ambiguous and conflicting date cues are flagged for review. SQLite stores account records, hashed passwords, session-token hashes and extracted checklist data. Uploaded PDF bytes remain in the active Streamlit session and are not saved to disk by default.

The web-facing listener is Nginx on port 3000. It proxies Streamlit on port 3001 and serves `/api/health` and `/manus-routes.json` directly. This preserves the 3000 port expected by Preview while keeping Streamlit as the application UI.

## Run locally

Requires Python 3.11+, Nginx, and (optional) Tesseract OCR. On Debian/Ubuntu:

```bash
sudo apt-get update
sudo apt-get install -y nginx tesseract-ocr
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
python start.py
```

Open `http://localhost:3000`. The first user can create an account. SQLite defaults to `data/actacite.sqlite3`; override it with `ACTACITE_DB_PATH` if needed. The local SQLite file is intentionally ignored by Git. Tests run with `.venv/bin/pytest -q`. Old local databases may retain unused reminder tables from an earlier schema; this version does not expose or process them.

For direct Streamlit development without the Nginx proxy, run `streamlit run app.py --server.address=127.0.0.1 --server.port=3001`; the health and route-manifest endpoints are available only through the proxy entry point.

## PDF handling

Only files with a `.pdf` name and PDF magic header are accepted. Files are capped at 50 MB and 300 pages. Password-protected or damaged documents are rejected. Official notice/schedule classification is conservative; notes, lecture material, uncertain document types, and sources without institutional signals are not processed. Deadlines require an explicit year; multiple dates in one sentence and differing deadlines for the same event are sent to human review instead of silently resolved. Date-only deadlines appear on the calendar at 11:59 PM in Asia/Kolkata; verify the source notice for exact times.

Evidence is rendered from the original page while its bytes remain in the current session. Selectable text is highlighted when a reliable match is found. For OCR-only pages or text whose location cannot be matched safely, the app shows the quote and page and explicitly reports that no reliable highlight was drawn. PDF bytes are not retained across sessions, so a user may need to re-upload a source to reopen it later.

## Calendar deadlines

All defensible dates extracted from official PDFs are listed on the Calendar with their task and source evidence. This version has no reminder settings or email, SMS, or push delivery worker; Calendar is the deadline tracking surface.

## Prototype security and operating limits

Passwords are stored as PBKDF2-HMAC-SHA256 hashes with per-user random salts. Random session tokens are stored only as hashes in SQLite with a seven-day expiration, and the token is held in Streamlit's server-side session state. This is a functional hackathon authentication flow, not an independent security audit. Do not use it for sensitive production accounts without stronger session-cookie controls, CSRF protection, rate limiting, account recovery, and a privacy review.

The Webdev app uses local SQLite and server disk for this MVP. That does not provide durable multi-instance production storage and may not survive replacement/redeployment. The managed Webdev database remains disabled to honor the PPT's SQLite/local-first choice. Publishing is not performed by this project setup.

The extraction pipeline is deterministic and rule-based; a pretrained LLM is not required or represented as having run. It may miss complex or multilingual notices. Always verify the evidence and review flags against the original official PDF.
