# ActaCite — Implementation Plan

## Product direction

ActaCite turns college notices into evidence-linked action checklists. Every task should answer what to do and by when, retain its exact source quote and page, and show uncertainty or conflicting instructions instead of silently guessing. The original notice remains the source of truth.

## Stack and implementation approach

Follow the PPT's proposed 24-hour MVP stack: Python for core logic; Streamlit for the interface; PyMuPDF for selectable PDF text; Tesseract OCR as a scanned-page fallback; regex/date parsing and spaCy's rule-based sentence splitting for candidate fields; source-quote/page evidence; structured task records; and SQLite/local session state. The PPT describes a pretrained LLM as optional, so the delivered baseline uses deterministic rules and does not claim an LLM parsed the notice.

The upload interface accepts PDF files only. A conservative document classifier accepts official notices, schedules, or timetables with institutional context and rejects Notes/study material and uncertain/non-notice documents. Notes rejection shows exactly: “Upload Denied: This document is not suitable for extracting schedule or notice information.” Candidate actions, explicit-year dates, eligibility conditions, and required-document cues are tied to their exact source sentence and page. Dates without an explicit year, multiple dates in one sentence, tentative/revised cues, and differing dates for the same event/deadline are flagged for review rather than silently resolved. Broader semantic extraction and all conflict types remain human-review limitations. Priority is based on time until a defensible deadline (high/red: 3 days or less; medium/yellow-orange: 4–14 days; low/green: over 14 days); undated tasks are medium with a provisional-priority note.

Sign-up/sign-in uses the requested name/email/password flow. Passwords are stored only as salted PBKDF2-HMAC-SHA256 hashes; SQLite stores unique user records and hashes of expiring session tokens, plus extracted checklist items. Uploaded PDFs remain in memory for the active Streamlit session/evidence viewer and are not retained by default. “Give Evidence” renders the cited source page and overlays a highlight when reliable PDF text coordinates can be found; when they cannot, the UI keeps the quote/page visible and says no reliable highlight was drawn.

The interface has a task-first dashboard, status controls and filters, an interactive calendar, document list, and evidence viewer. Per the user's fallback choice, the app has no reminder settings, phone/email fields, notification subscriptions, or scheduled message delivery. Extracted deadlines are displayed directly on the calendar with their evidence association; date-only entries are placed at 11:59 PM Asia/Kolkata and should be checked against the source.

## Runtime and persistence constraints

The initialized Webdev project has its managed server enabled and managed database disabled, matching the PPT's SQLite/local-first design. Nginx listens on port 3000 and proxies Streamlit on 3001; it also serves health and route-manifest endpoints. SQLite gives this MVP local persistence, but a container-local SQLite file is not durable multi-instance production storage and may not survive replacement or redeployment. This plan therefore targets a working hackathon prototype/Preview, not production-grade hosted accounts. The website is not published by this work.

## Project structure

- `app.py` — Streamlit sign-in/sign-up, dashboard, PDF upload, checklist, calendar and evidence viewer.
- `actacite/auth.py` — signup/sign-in, password hashing and session helpers.
- `actacite/pdf_ingest.py` — PDF validation, page-aware text extraction and Tesseract OCR fallback.
- `actacite/classifier.py` — conservative official-notice/schedule versus Notes/other classification.
- `actacite/extractor.py` — deterministic task, date, eligibility and required-document cues; date and conflict review flags.
- `actacite/evidence.py` — cited-page rendering and safe source-text highlighting.
- `actacite/storage.py` — SQLite schema and scoped access; no uploaded-PDF archive.
- `static/` — browser icon and the Webdev route manifest.
- `tests/` — focused classification, extraction, auth and evidence checks.
- `requirements.txt`, `.streamlit/config.toml`, `Dockerfile`, `nginx.conf`, `start.py` — pinned dependencies, Streamlit runtime settings, container, proxy and launcher.
- `app.config.ts` — platform logo URL metadata.

## Design system

### Styles considered

- Evidence-first editorial dashboard (chosen): warm administrative-paper surfaces, crisp citations and a focused task list. Probability: 0.0821.
- Alpine academic laboratory: cooler slate panels, precise data tables, and restrained instrument-like controls. Probability: 0.0054.
- Civic service desk: softer colors and warmer, form-led wayfinding for campus support. Probability: 0.0276.

### Chosen style: Evidence-first editorial dashboard

- **Design movement:** Academic-administration clarity with the restraint of Swiss editorial layouts.
- **Core principles:** Source before summary; make actions scannable; keep uncertainty explicit; use color consistently for priority and verification.
- **Color philosophy:** Warm paper and pale blue-neutral surfaces keep long notices approachable; deep navy anchors trust; orange signals time-sensitive action and primary actions; teal marks citations/evidence. High, medium and low priorities stay visually distinct.
- **Layout paradigm:** A compact dark navigation rail, a broad working surface, a compact metric strip and a single-column action list; evidence opens in context rather than hiding the source in a generic card grid.
- **Signature elements:** Quote-and-page evidence bars; a colored priority rail on each task; a teal ActaCite A/check mark.
- **Interaction philosophy:** Every extracted item offers “Give Evidence”; uncertain items explain why they need review; uploads show progress and explicit acceptance/rejection feedback.
- **Animation:** Restrained 160–180 ms transitions for controls and task-card hover; no motion on rendered source highlights; honor `prefers-reduced-motion`.
- **Typography:** DM Sans for interface labels and body copy, Source Serif 4 for quoted notice text and editorial headings; hierarchy through scale, weight, and comfortable line length.
- **Brand essence:** A practical notice-to-action companion for students and campus teams; precise, calm, accountable.
- **Brand voice:** Direct, supportive, evidence-led. Example lines: “Your next step, with the source attached.” “This date is unclear in the notice—check the original before acting.”
- **Wordmark & logo:** ActaCite wordmark paired with a compact teal A and a small orange verification tick.
- **Signature brand color:** Acta Teal, used for citations and the mark.

## Build workflow

The original plan was approved before implementation and subsequently narrowed by the user to calendar-only deadline tracking because no SMS gateway was authorized/configured. `TODO.md` preserves the requested behavior clauses and leaves broader semantic/conflict validation open. The app and route manifest are active in Preview; publishing remains off.
