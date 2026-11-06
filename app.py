from __future__ import annotations

import calendar
import hashlib
import html
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import streamlit as st

from actacite import auth, storage
from actacite.classifier import classify_document
from actacite.evidence import render_evidence_page
from actacite.extractor import extract_tasks
from actacite.pdf_ingest import extract_pdf, validate_pdf
TZ = ZoneInfo("Asia/Kolkata")
NOTES_DENIAL = "Upload Denied: This document is not suitable for extracting schedule or notice information."

st.set_page_config(page_title="ActaCite · Notice intelligence", page_icon="static/actacite-mark.png", layout="wide", initial_sidebar_state="collapsed")
st.markdown(
    """
    <style>
      @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Source+Serif+4:wght@500;600&display=swap');
      :root { --ink:#18283b; --muted:#6e7b89; --paper:#f7f5f1; --line:#e9e6df; --orange:#d96d2d; --teal:#148f87; --blue:#5579ad; }
      html, body, [class*="css"] { font-family:'DM Sans',sans-serif; color:var(--ink); }
      .stApp { background:linear-gradient(180deg,#fbfaf8 0%,#f7f5f1 100%); }
      .block-container { max-width:1420px; padding-top:1.25rem; padding-bottom:3rem; }
      [data-testid="stSidebar"] { background:#172638; }
      [data-testid="stSidebar"] * { color:#f3f6f8 !important; }
      [data-testid="stSidebar"] .stButton button { text-align:left; border:1px solid transparent; background:transparent; color:#dfe7eb; }
      [data-testid="stSidebar"] .stButton button:hover { background:#24394f; border-color:#38536e; }
      h1,h2,h3 { color:#18283b; letter-spacing:-.035em; }
      h1 { font-size:2.05rem !important; font-weight:700 !important; }
      h2 { font-size:1.36rem !important; font-weight:700 !important; }
      .brand-lockup { display:flex; align-items:center; gap:11px; margin:0 0 1.4rem; }
      .brand-mark { width:38px;height:38px;border-radius:13px;background:#148f87;color:white;display:grid;place-items:center;font:700 21px 'Source Serif 4',serif;box-shadow:0 6px 14px #148f872e; }
      .brand-name { font-size:20px;font-weight:700;letter-spacing:-.04em;color:#172638; }
      .brand-sub { font-size:10px;letter-spacing:.16em;text-transform:uppercase;color:#84919d;font-weight:700;margin-top:1px; }
      .hero { background:#172638; border-radius:22px; padding:28px 32px; color:white; position:relative; overflow:hidden; margin:0 0 20px; box-shadow:0 14px 35px #1c30421b; }
      .hero:after { content:''; position:absolute; right:-70px; top:-155px; width:340px;height:340px;border:1px solid #ffffff17;border-radius:50%;box-shadow:0 0 0 32px #ffffff08,0 0 0 66px #ffffff06; }
      .hero-kicker { color:#f2aa69; font-size:11px; letter-spacing:.17em; text-transform:uppercase; font-weight:700; margin-bottom:8px; }
      .hero-title { font:600 31px 'Source Serif 4',serif; color:#fff; letter-spacing:-.03em; margin:0 0 8px; }
      .hero-copy { color:#c4d0da; font-size:14px; max-width:700px; margin:0; }
      .eyebrow { text-transform:uppercase;letter-spacing:.14em;font-size:10px;color:#8794a1;font-weight:700; }
      .section-head { display:flex;align-items:center;justify-content:space-between;gap:12px;margin:10px 0 13px; }
      .section-head h2 { margin:0; }
      .metric-card { background:#fff;border:1px solid var(--line);border-radius:16px;padding:15px 17px;min-height:98px;box-shadow:0 4px 12px #29384707; }
      .metric-label { color:#74808c;font-size:11px;font-weight:600; }
      .metric-value { color:#172638;font-size:26px;font-weight:700;line-height:1.1;margin-top:7px; }
      .metric-note { color:#a0a8af;font-size:11px;margin-top:4px; }
      .task-card { background:#fff;border:1px solid #e7e4dd;border-radius:16px;padding:17px 18px 14px;margin-bottom:10px;box-shadow:0 4px 14px #25364708;position:relative;overflow:hidden;transition:transform 180ms ease,box-shadow 180ms ease,border-color 180ms ease; }
      .task-card:hover { transform:translateY(-1px);box-shadow:0 8px 20px #25364710; }
      .task-card.high { border-left:4px solid #d75e57; }
      .task-card.medium { border-left:4px solid #e4a638; }
      .task-card.low { border-left:4px solid #36a47a; }
      .task-title { font-size:15px;font-weight:700;line-height:1.45;color:#192b3e;margin-bottom:8px; }
      .task-meta { font-size:12px;color:#667482;line-height:1.6; }
      .source-quote { background:#f5f7f7;border-left:2px solid #148f87;padding:9px 11px;border-radius:0 8px 8px 0;font:500 12px 'Source Serif 4',serif;color:#43505c;margin-top:10px;line-height:1.55; }
      .priority-pill { display:inline-block;padding:4px 9px;border-radius:999px;font-size:10px;letter-spacing:.04em;font-weight:700;text-transform:uppercase; }
      .priority-pill.high { background:#fff0ed;color:#bb4f46; }
      .priority-pill.medium { background:#fff6df;color:#9c6a08; }
      .priority-pill.low { background:#eaf7f1;color:#207d5b; }
      .review-note { color:#965a11;background:#fff6e7;border-radius:8px;padding:8px 10px;font-size:11px;margin-top:9px; }
      .upload-card { border:1.5px dashed #d4d0c7;background:#fffdfa;border-radius:18px;padding:20px 22px;margin:16px 0 20px; }
      .upload-title { font-size:15px;font-weight:700;color:#1c2e40; }
      .upload-copy { color:#74808c;font-size:12px;margin-top:3px; }
      .calendar-head { font-size:12px;color:#7d8a95;text-align:center;padding:8px 0;font-weight:700;text-transform:uppercase; }
      .calendar-day { text-align:center;padding:7px 3px;color:#263746;font-size:12px; }
      .calendar-day.muted { color:#bac1c7; }
      .calendar-dot { width:5px;height:5px;background:#d96d2d;border-radius:50%;display:inline-block;margin:0 1px; }
      .calendar-dot.teal { background:#148f87; }
      .empty-state { border:1px dashed #d7d4cd;background:#fff;border-radius:16px;padding:28px;text-align:center;color:#74808c; }
      .empty-state strong { color:#314154;display:block;margin-bottom:4px; }
      .evidence-label { color:#148f87;font-size:10px;letter-spacing:.12em;text-transform:uppercase;font-weight:700; }
      .auth-shell { max-width:520px;margin:6vh auto 0; }
      .auth-card { background:white;border:1px solid #e8e4dc;border-radius:22px;padding:25px 28px;box-shadow:0 20px 50px #2335480d; }
      div[data-testid="stMetric"] { background:#fff;border:1px solid var(--line);padding:12px 15px;border-radius:14px; }
      .stButton button[kind="primary"] { background:#d96d2d;border-color:#d96d2d; }
      .stButton button { border-radius:10px;transition:background-color 160ms ease,border-color 160ms ease,transform 160ms ease; }
      .stTextInput input, .stSelectbox div[data-baseweb="select"], .stMultiSelect div[data-baseweb="select"] { border-radius:10px; }
      .stAlert { border-radius:12px; }
      @media (prefers-reduced-motion:reduce) { *,*::before,*::after { animation:none !important;transition:none !important;scroll-behavior:auto !important; } }
      footer { visibility:hidden; }
    </style>
    """,
    unsafe_allow_html=True,
)

storage.init_db()


def _brand(sidebar: bool = False) -> None:
    st.markdown(
        '<div class="brand-lockup"><div class="brand-mark">A</div><div><div class="brand-name">ActaCite</div><div class="brand-sub">Notice intelligence</div></div></div>',
        unsafe_allow_html=True,
    )


def _start_session(user_id: str) -> None:
    st.session_state["actacite_session"] = auth.new_session(user_id)
    st.session_state["active_page"] = "Dashboard"


def _login_view() -> None:
    left, center, right = st.columns([1, 1.04, 1])
    with center:
        st.markdown('<div class="auth-shell">', unsafe_allow_html=True)
        _brand()
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)
        st.markdown("### Your next step, with the source attached.")
        st.caption("Turn official campus notices into clear, verifiable actions.")
        sign_in_tab, sign_up_tab = st.tabs(["Sign in", "Create account"])
        with sign_in_tab:
            with st.form("signin_form", clear_on_submit=False):
                email = st.text_input("Email", placeholder="you@college.edu", key="signin_email")
                password = st.text_input("Password", type="password", key="signin_password")
                submitted = st.form_submit_button("Sign in", type="primary", use_container_width=True)
            if submitted:
                ok, user = auth.verify_credentials(email, password)
                if ok and user:
                    _start_session(user["id"])
                    st.rerun()
                else:
                    st.error("Email or password is incorrect.")
        with sign_up_tab:
            with st.form("signup_form", clear_on_submit=True):
                name = st.text_input("Name", placeholder="Your name")
                email = st.text_input("Email", placeholder="you@college.edu", key="signup_email")
                password = st.text_input("Password", type="password", help="At least 10 characters.", key="signup_password")
                confirm = st.text_input("Confirm password", type="password", key="signup_confirm")
                submitted = st.form_submit_button("Create account", type="primary", use_container_width=True)
            if submitted:
                if password != confirm:
                    st.error("Passwords do not match.")
                else:
                    ok, message, user_id = auth.sign_up(name, email, password)
                    if ok and user_id:
                        _start_session(user_id)
                        st.success("Account created. Your workspace is ready.")
                        st.rerun()
                    else:
                        st.error(message)
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('<p style="text-align:center;color:#87919a;font-size:11px;margin-top:13px">Your uploads stay in this session; ActaCite stores the evidence-linked checklist, not your PDF.</p>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


def _priority_chip(priority: str) -> str:
    label = {"high": "High priority", "medium": "Medium priority", "low": "Low priority"}.get(priority, "Review")
    return f'<span class="priority-pill {html.escape(priority)}">{label}</span>'


def _due_text(due_at: str | None) -> str:
    if not due_at:
        return "No deadline found"
    try:
        due = datetime.fromisoformat(due_at).astimezone(TZ)
        return due.strftime("%a, %d %b %Y")
    except ValueError:
        return due_at


def _load_uploaded_files(user_id: str) -> None:
    uploads = st.file_uploader(
        "Choose official notice PDFs",
        type=["pdf"],
        accept_multiple_files=True,
        help="PDF only · up to 50 MB each · text and scanned PDFs supported when OCR is available.",
        key="notice_uploader",
        label_visibility="collapsed",
    )
    if not uploads:
        return
    handled: set[str] = st.session_state.setdefault("handled_upload_hashes", set())
    documents: dict[str, dict] = st.session_state.setdefault("active_documents", {})
    for upload in uploads:
        payload = upload.getvalue()
        digest = hashlib.sha256(payload).hexdigest()
        if digest in handled:
            continue
        handled.add(digest)
        try:
            validate_pdf(upload.name, payload)
            with st.spinner(f"Reading and checking {upload.name}…"):
                extracted = extract_pdf(payload)
                full_text = "\n".join(extracted.pages)
                classification = classify_document(full_text)
            if not classification.accepted:
                if classification.category == "notes":
                    st.session_state["rejection"] = {"message": NOTES_DENIAL, "notes": True}
                else:
                    st.session_state["rejection"] = {
                        "message": f"Upload not accepted: {classification.reason} Please upload an official college/office notice, schedule, or timetable.",
                        "notes": False,
                    }
                continue
            records = extract_tasks(extracted.pages, digest, upload.name)
            documents[digest] = {
                "name": upload.name,
                "bytes": payload,
                "pages": extracted.page_count,
                "ocr_pages": sorted(extracted.ocr_pages),
                "classification": classification.category,
            }
            saved = 0
            for task in records:
                storage.save_task(user_id, task)
                saved += 1
            if saved:
                st.session_state["upload_notice"] = f"{saved} evidence-linked item{'s' if saved != 1 else ''} extracted from {upload.name}."
                st.rerun()
            else:
                st.session_state["upload_notice"] = f"{upload.name} was verified as an official notice, but no defensible action or date was found. Review the original document manually."
        except Exception as exc:
            st.session_state["upload_notice"] = f"{upload.name}: {exc}"


def _notes_modal() -> None:
    @st.dialog("Upload denied", width="small")
    def show(message: str) -> None:
        st.error(message, icon="⛔")
        st.write("ActaCite only processes official notices, schedules, and timetables—not study material.")
        if st.button("Close", type="primary", use_container_width=True):
            st.session_state.pop("rejection", None)
            st.rerun()
    rejection = st.session_state.get("rejection")
    if rejection:
        show(rejection["message"])


@st.dialog("Give Evidence", width="large")
def _evidence_dialog(task: dict) -> None:
    document = st.session_state.get("active_documents", {}).get(task["document_hash"])
    st.markdown(f'<div class="evidence-label">{html.escape(task["document_name"])} · page {task["source_page"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="source-quote">“{html.escape(task["source_quote"])}”</div>', unsafe_allow_html=True)
    if document:
        try:
            rendered = render_evidence_page(document["bytes"], int(task["source_page"]), task["source_quote"])
            st.caption(rendered.message)
            st.image(rendered.image, use_container_width=True)
            st.download_button("Download original PDF", document["bytes"], file_name=document["name"], mime="application/pdf", key=f"download_{task['id']}")
        except Exception as exc:
            st.warning(str(exc))
    else:
        st.info("The original PDF is not retained after the active session. Re-upload it to view and highlight this source page.")
    if st.button("Done", use_container_width=True):
        st.session_state.pop("selected_evidence", None)
        st.rerun()


def _task_card(task: dict, user_id: str, compact: bool = False) -> None:
    priority = task["priority"]
    review = task.get("review_note", "")
    quote = html.escape(task["source_quote"])
    title = html.escape(task["title"])
    page = task["source_page"]
    due = html.escape(_due_text(task.get("due_at")))
    status = task["status"]
    st.markdown(
        f'<div class="task-card {html.escape(priority)}"><div style="display:flex;align-items:flex-start;justify-content:space-between;gap:12px"><div class="task-title">{title}</div>{_priority_chip(priority)}</div>'
        f'<div class="task-meta">{due} &nbsp;·&nbsp; {html.escape(task["document_name"])} &nbsp;·&nbsp; page {page}</div>'
        f'<div class="source-quote">“{quote}”</div>'
        f'{f"<div class=review-note>{html.escape(review)}</div>" if review else ""}</div>',
        unsafe_allow_html=True,
    )
    if not compact:
        left, right = st.columns([1, 1])
        with left:
            if st.button("Give Evidence", key=f"evidence_{task['id']}", use_container_width=True):
                st.session_state["selected_evidence"] = task["id"]
                st.rerun()
        with right:
            action = "Mark complete" if status == "open" else "Reopen"
            if st.button(action, key=f"status_{task['id']}", use_container_width=True):
                storage.set_task_status(user_id, task["id"], "done" if status == "open" else "open")
                st.rerun()


def _metric(label: str, value: str, note: str) -> None:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{html.escape(label)}</div><div class="metric-value">{html.escape(value)}</div><div class="metric-note">{html.escape(note)}</div></div>',
        unsafe_allow_html=True,
    )


def _dashboard(user: dict) -> None:
    user_id = user["id"]
    name = user["name"].split()[0]
    now = datetime.now(TZ)
    st.markdown(
        f'<section class="hero"><div class="hero-kicker">Your campus, in the clear</div><div class="hero-title">Good to see you, {html.escape(name)}.</div><p class="hero-copy">Find the next step in every official notice—and keep the source quote one click away.</p></section>',
        unsafe_allow_html=True,
    )
    tasks = storage.list_tasks(user_id)
    open_tasks = [task for task in tasks if task["status"] == "open"]
    high = [task for task in open_tasks if task["priority"] == "high"]
    dated_soon = [task for task in open_tasks if task["due_at"] and datetime.fromisoformat(task["due_at"]) <= now + timedelta(days=7)]
    docs = len({task["document_hash"] for task in tasks})
    m1, m2, m3, m4 = st.columns(4)
    with m1: _metric("Open actions", str(len(open_tasks)), "Evidence-linked checklist")
    with m2: _metric("Imminent", str(len(high)), "High priority · 3 days or less")
    with m3: _metric("Due this week", str(len(dated_soon)), "From cited dates")
    with m4: _metric("Notices processed", str(docs), "PDFs analyzed in this account")

    st.markdown('<div class="section-head"><h2>Bring in a notice</h2><span class="eyebrow">PDF only · official sources</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="upload-card"><div class="upload-title">Drop a college or office notice here</div><div class="upload-copy">We read the PDF, verify each extracted action against its quote and page, and flag anything unclear.</div></div>', unsafe_allow_html=True)
    _load_uploaded_files(user_id)
    if st.session_state.get("upload_notice"):
        st.info(st.session_state.pop("upload_notice"))

    st.markdown('<div class="section-head"><h2>Your action list</h2><span class="eyebrow">Every task has a source</span></div>', unsafe_allow_html=True)
    if not tasks:
        st.markdown('<div class="empty-state"><strong>No evidence-linked tasks yet</strong>Upload an official PDF to build your first checklist. Notes and study materials are rejected.</div>', unsafe_allow_html=True)
        return
    filter_choice = st.selectbox("Show", ["Open tasks", "All tasks", "Completed"], label_visibility="collapsed", key="task_filter")
    shown = open_tasks if filter_choice == "Open tasks" else tasks if filter_choice == "All tasks" else [task for task in tasks if task["status"] == "done"]
    if not shown:
        st.info("Nothing in this view yet.")
    for task in shown:
        _task_card(task, user_id)


def _calendar_page(user: dict) -> None:
    user_id = user["id"]
    tasks = [task for task in storage.list_tasks(user_id) if task["due_at"]]
    if "calendar_month" not in st.session_state:
        today = datetime.now(TZ).date()
        st.session_state["calendar_month"] = date(today.year, today.month, 1)
    month: date = st.session_state["calendar_month"]
    title_col, prev_col, next_col = st.columns([5, 1, 1])
    with title_col:
        st.markdown(f"## {month.strftime('%B %Y')}")
    with prev_col:
        if st.button("←", key="calendar_prev", use_container_width=True):
            st.session_state["calendar_month"] = date(month.year - (month.month == 1), 12 if month.month == 1 else month.month - 1, 1)
            st.rerun()
    with next_col:
        if st.button("→", key="calendar_next", use_container_width=True):
            st.session_state["calendar_month"] = date(month.year + (month.month == 12), 1 if month.month == 12 else month.month + 1, 1)
            st.rerun()
    st.caption("Dates are parsed from source quotes. Date-only entries are placed at 11:59 PM Asia/Kolkata; confirm the original notice for exact timing.")
    weekday_cols = st.columns(7)
    for col, day_name in zip(weekday_cols, ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
        with col: st.markdown(f'<div class="calendar-head">{day_name}</div>', unsafe_allow_html=True)
    month_grid = calendar.Calendar(firstweekday=0).monthdatescalendar(month.year, month.month)
    for week_no, week in enumerate(month_grid):
        cols = st.columns(7)
        for col, day in zip(cols, week):
            with col:
                day_tasks = [task for task in tasks if datetime.fromisoformat(task["due_at"]).astimezone(TZ).date() == day]
                is_current = day.month == month.month
                label = str(day.day) + ("  •" if day_tasks else "")
                if st.button(label, key=f"calendar_{day.isoformat()}", use_container_width=True, disabled=not is_current):
                    st.session_state["selected_calendar_day"] = day.isoformat()
                if day_tasks:
                    st.caption(f"{len(day_tasks)} item{'s' if len(day_tasks) != 1 else ''}")
    selected = st.session_state.get("selected_calendar_day")
    if selected:
        chosen = date.fromisoformat(selected)
        items = [task for task in tasks if datetime.fromisoformat(task["due_at"]).astimezone(TZ).date() == chosen]
        st.markdown(f"### {chosen.strftime('%A, %d %B')}")
        if items:
            for task in items:
                _task_card(task, user_id, compact=True)
        else:
            st.caption("No cited deadlines on this date.")
    if not tasks:
        st.markdown('<div class="empty-state"><strong>Your calendar is clear</strong>Dates will appear here when a PDF contains a defensible deadline or important date.</div>', unsafe_allow_html=True)


def _documents_page(user: dict) -> None:
    tasks = storage.list_tasks(user["id"])
    grouped: dict[str, list[dict]] = {}
    for task in tasks:
        grouped.setdefault(task["document_hash"], []).append(task)
    st.markdown("## Documents")
    st.caption("ActaCite stores parsed checklist data and source references. Uploaded PDF bytes remain in the active browser session only.")
    if not grouped:
        st.markdown('<div class="empty-state"><strong>No notices processed</strong>Accepted PDFs will be listed here after extraction.</div>', unsafe_allow_html=True)
        return
    for digest, items in grouped.items():
        first = items[0]
        with st.container(border=True):
            active = st.session_state.get("active_documents", {}).get(digest)
            st.markdown(f"### {html.escape(first['document_name'])}")
            st.caption(f"{len(items)} evidence-linked item{'s' if len(items) != 1 else ''} · SHA-256 {digest[:12]}…")
            if active:
                st.caption(f"Available in this session · {active['pages']} pages · {active['classification'].replace('_',' ').title()}")
                st.download_button("Download original PDF", active["bytes"], file_name=active["name"], mime="application/pdf", key=f"docdownload_{digest}")
            else:
                st.info("Source file not retained. Re-upload this PDF to reopen its cited pages.")


def main() -> None:
    token = st.session_state.get("actacite_session")
    user = auth.current_user(token)
    if not user:
        if token:
            auth.end_session(token)
            st.session_state.pop("actacite_session", None)
        _login_view()
        _notes_modal()
        return

    with st.sidebar:
        _brand(sidebar=True)
        st.markdown(f"<div style='color:#b7c7d2;font-size:12px;margin:-10px 0 20px'>{html.escape(user['name'])}<br><span style='color:#8295a5'>{html.escape(user['email'])}</span></div>", unsafe_allow_html=True)
        nav_items = ["Dashboard", "Calendar", "Documents"]
        for item in nav_items:
            if st.button(("●  " if st.session_state.get("active_page", "Dashboard") == item else "○  ") + item, key=f"nav_{item}", use_container_width=True):
                st.session_state["active_page"] = item
                st.rerun()
        st.markdown("<div style='height:18vh'></div><div style='border-top:1px solid #35495c;padding-top:14px;color:#9fb0bc;font-size:11px'>Evidence first.<br>Always within reach.</div>", unsafe_allow_html=True)
        if st.button("Sign out", key="signout", use_container_width=True):
            auth.end_session(token)
            st.session_state.pop("actacite_session", None)
            st.session_state.pop("active_documents", None)
            st.session_state.pop("handled_upload_hashes", None)
            st.rerun()

    page = st.session_state.get("active_page", "Dashboard")
    if page not in {"Dashboard", "Calendar", "Documents"}:
        page = "Dashboard"
        st.session_state["active_page"] = page
    if page == "Dashboard":
        _dashboard(user)
    elif page == "Calendar":
        _calendar_page(user)
    elif page == "Documents":
        _documents_page(user)

    selected_id = st.session_state.get("selected_evidence")
    if selected_id:
        selected = next((task for task in storage.list_tasks(user["id"]) if task["id"] == selected_id), None)
        if selected:
            _evidence_dialog(selected)
        else:
            st.session_state.pop("selected_evidence", None)
    _notes_modal()


main()
