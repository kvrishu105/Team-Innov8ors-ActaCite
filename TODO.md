# ActaCite build outcomes

## Secure account access
- [x] Provide secure Sign Up and Sign In views with Name, Email, and Password inputs. Existing users can Sign In; new users can Create Account. Persist session state securely. Passwords are stored as per-user salted PBKDF2-HMAC-SHA256 hashes, email addresses are unique, and expiring random application sessions are stored as token hashes in SQLite. This is a functional MVP, not an independent security audit.

## PDF-only upload and strict document classification
- [x] Provide a prominent upload zone that accepts only `.pdf` files. The uploader limits selectable files to PDFs; backend validation checks the extension, PDF signature, size, page count, and password protection.
- [x] Analyze uploaded PDF content and accept only official notices, schedules, or timetables with institutional/issuing-office context. Reject uncertain or non-notice materials conservatively.
- [x] Strictly reject PDFs classified as Notes or study material. When a Notes PDF is uploaded, show a prominent modal with the exact text: “Upload Denied: This document is not suitable for extracting schedule or notice information.”
- [x] Keep uploaded PDFs transient for the active session/evidence viewer and do not retain uploaded notices by default. Persist parsed checklist items and settings rather than source PDF bytes.

## Evidence-grounded extraction and uncertainty handling
- [x] For accepted notices/schedules, extract action items, explicit-year deadlines and important dates, eligibility conditions, and required-document cues where the rules recognize them. This is deterministic cue-based extraction, not broad semantic or multilingual document understanding.
- [x] Retain an exact source quote and source page for every extracted point; show evidence beside every task so a reviewer can verify it against the original without searching the full document.
- [ ] Validate every extracted field against its source. If a date or detail is missing, ambiguous, conflicting, or unsupported, flag it for human review instead of guessing or silently inventing an answer. Missing-year dates, multiple dates in one sentence, explicit tentative/revised cues, and different dates for the same event/deadline are flagged. Broad field-level semantic and eligibility-conflict checks remain incomplete.
- [x] Display extracted tasks cleanly as cards in a task-first checklist, not as a paragraph-only summary.
- [x] Categorize tasks by time sensitivity: High priority (red) for imminent deadlines/short time to complete (3 days or less); Medium priority (yellow/orange) for normal time (4–14 days); Low priority (green) for long runway (over 14 days). Do not fabricate a deadline when the source omits a year or contains multiple dates; mark undated items Medium with a provisional-priority review note.

## Give Evidence PDF viewer
- [x] Beside each extracted important detail, provide a “Give Evidence” button.
- [x] Clicking “Give Evidence” opens an in-app viewer showing the original PDF's cited page. The page is rendered as an image and the original PDF can be downloaded while its bytes remain in the active session; if the bytes are no longer available, explain that the source must be re-uploaded.
- [x] Visually highlight the specific source text/region corresponding to the extracted point when reliable PDF text coordinates can be located. If a match cannot be reliably located, state that no safe highlight was drawn and keep the quote/page evidence visible.

## Deadline calendar
- [x] Integrate an interactive calendar view within the dashboard.
- [x] Automatically populate the calendar with defensible deadlines and important dates extracted from uploaded PDFs, retaining the source evidence association. Dates without an explicit year or with multiple dates in one sentence are left for review rather than guessed onto the calendar.

## Calendar-only deadline tracking
- [x] Populate Calendar directly with defensible deadlines and important dates extracted from official PDFs, retaining the associated task and source evidence.
- [x] Per the user's fallback choice, remove the Reminder settings page, phone/email delivery fields, notification controls, and scheduled message delivery; this version marks deadlines on Calendar only and does not claim email, SMS, or push delivery.
- [x] Keep date-only events visible at 11:59 PM Asia/Kolkata and direct the user to verify the exact time in the original notice.

## PPT architecture and MVP boundaries
- [x] Implement the PPT's Python core logic and Streamlit interface; use PyMuPDF for PDF text extraction, Tesseract OCR for scanned pages when available, regex/date parsing and spaCy's rule-based sentence splitting for candidate dates/actions/conditions, evidence quotes with source page, and structured persisted task records. A pretrained LLM was optional in the PPT and is not used by this deterministic baseline.
- [x] Preserve the PPT's pipeline: PDF input → read PDF text/OCR → clean and split text → extract dates/tasks/rules → keep the evidence quote and page → task checklist.
- [x] Use session state and SQLite/local-first storage for checklist state as needed; avoid storing uploaded notices by default.
- [ ] Keep the original college notice as the source of truth; explain what it says without replacing it, and flag unclear/conflicting statements for human review. Missing-year dates, multi-date sentences, explicit revisions/tentative cues, and differing repeated event deadlines are flagged; comprehensive conflict resolution remains incomplete.
- [x] Provide loading states, error handling, and clear empty, accepted, rejected, review-needed, and success states for interactions.
- [x] Keep scope focused on a functional hackathon MVP; do not publish or represent the SQLite prototype as durable multi-instance production hosting unless the user explicitly asks for that next step.
