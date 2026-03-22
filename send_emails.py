"""
Nest Navigate Outreach - Email Drafter
Reads leads.csv rows 151-200, generates AI brand fit, creates Gmail drafts,
and updates the leads Google Sheet.
"""

import csv
import html as html_lib
import os
import base64
import logging
import time
from datetime import datetime, date
from email.mime.text import MIMEText
from pathlib import Path

import anthropic
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.StreamHandler()],
)
log = logging.getLogger(__name__)

BATCH_START = 150   # 0-indexed, so rows 151-200
BATCH_END   = 200
BATCH_SIZE  = 50

_SIGNATURE_SENTINEL = "__EMAIL_SIG__"

# Load Claude API key
_key_path = Path("Claude NN Key.txt")
CLAUDE_API_KEY = _key_path.read_text().strip() if _key_path.exists() else os.environ.get("ANTHROPIC_API_KEY", "")


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def get_credentials():
    creds = None
    if os.path.exists(config.TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(config.TOKEN_FILE, config.GMAIL_SCOPES)
        # If the saved token is missing any required scope, nuke it and re-auth
        if creds and creds.scopes and not set(config.GMAIL_SCOPES).issubset(set(creds.scopes)):
            log.info("Token missing required scopes - re-authenticating...")
            os.remove(config.TOKEN_FILE)
            creds = None
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(config.CREDENTIALS_FILE, config.GMAIL_SCOPES)
            creds = flow.run_local_server(port=0)
        with open(config.TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return creds


def get_gmail_service():
    return build("gmail", "v1", credentials=get_credentials())


def get_sheets_service():
    return build("sheets", "v4", credentials=get_credentials())


# ---------------------------------------------------------------------------
# Gmail signature
# ---------------------------------------------------------------------------

def get_gmail_signature(service) -> str:
    try:
        result = service.users().settings().sendAs().list(userId="me").execute()
        for send_as in result.get("sendAs", []):
            if send_as.get("isPrimary"):
                return send_as.get("signature", "")
    except Exception as e:
        log.warning(f"Could not fetch Gmail signature: {e}")
    return ""


# ---------------------------------------------------------------------------
# AI brand fit
# ---------------------------------------------------------------------------

def generate_ai_brand_fit(lead: dict) -> str:
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    company  = lead.get("Company Name", "")
    industry = lead.get("Industry", "")
    keywords = lead.get("Keywords", "")[:600]
    title    = lead.get("Title", "")

    prompt = f"""Write exactly 1 sentence explaining why {company} ({industry}) is a natural fit for first-time homebuyers as a rewards partner on the Nest Navigate platform.

Context:
- Company: {company}
- Industry: {industry}
- Title of contact: {title}
- Keywords: {keywords}

Rules:
- 1 sentence only
- Be specific to this company and industry
- Connect to first-time homebuyers naturally acquiring this type of product/service
- No fluff, no filler
- Do not start with "I" or mention Nest Navigate
- Do not use em dashes"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=100,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text.strip()
    # Strip any em dashes that slip through
    return text.replace("\u2014", "-")


# ---------------------------------------------------------------------------
# Template
# ---------------------------------------------------------------------------

def load_template(touch_number: int) -> dict:
    path = Path("templates_v2") / f"touch{touch_number}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {path}")
    content = path.read_text()
    lines = content.strip().splitlines()
    subject_line = next((l for l in lines if l.lower().startswith("subject:")), None)
    subject = subject_line.split(":", 1)[1].strip()
    subject_idx = lines.index(subject_line)
    body = "\n".join(lines[subject_idx + 2:]).strip()
    return {"subject": subject, "body": body}


def render_html(template_body: str, template_subject: str, lead: dict, signature_html: str = "") -> tuple[str, str]:
    """Returns (subject, html_body)."""
    body = template_body
    subject = template_subject

    # Swap signature placeholder for sentinel before escaping
    body = body.replace("{{signature}}", _SIGNATURE_SENTINEL)

    # Render all lead fields and standard config vars into both subject and body
    for key, value in lead.items():
        placeholder = f"{{{{{key}}}}}"
        val = str(value) if value else ""
        body = body.replace(placeholder, val)
        subject = subject.replace(placeholder, val)

    for placeholder, val in [
        ("{{sender_name}}", config.SENDER_NAME),
        ("{{sender_title}}", config.SENDER_TITLE),
        ("{{website}}", config.WEBSITE_URL),
    ]:
        body = body.replace(placeholder, val)
        subject = subject.replace(placeholder, val)

    # Strip em dashes
    body = body.replace("\u2014", "-")
    subject = subject.replace("\u2014", "-")

    # HTML-escape the body (sentinel has no special HTML chars so it survives)
    escaped = html_lib.escape(body, quote=False)

    # Inject real HTML signature
    escaped = escaped.replace(_SIGNATURE_SENTINEL, signature_html)

    # Convert paragraph breaks then line breaks
    escaped = escaped.replace("\n\n", "</p><p>")
    escaped = escaped.replace("\n", "<br>")

    html_body = (
        '<html><body style="font-family:Arial,sans-serif;font-size:14px;color:#000000;line-height:1.5">'
        f"<p>{escaped}</p>"
        "</body></html>"
    )

    return subject, html_body


# ---------------------------------------------------------------------------
# Send log
# ---------------------------------------------------------------------------

def load_send_log() -> dict:
    log_data = {}
    path = Path(config.SEND_LOG_FILE)
    if not path.exists():
        return log_data
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            email = row["email"].lower()
            if email not in log_data:
                log_data[email] = {}
            log_data[email][int(row["touch"])] = datetime.strptime(row["sent_date"], "%Y-%m-%d").date()
    return log_data


def append_send_log(email: str, touch: int, sent_date: date):
    path = Path(config.SEND_LOG_FILE)
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.exists() or path.stat().st_size == 0
    with open(path, "a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["email", "touch", "sent_date"])
        writer.writerow([email.lower(), touch, sent_date.isoformat()])


# ---------------------------------------------------------------------------
# Gmail draft
# ---------------------------------------------------------------------------

def create_draft(service, to: str, subject: str, body_html: str):
    message = MIMEText(body_html, "html")
    message["to"]      = to
    message["from"]    = f"{config.SENDER_NAME} <{config.SENDER_EMAIL}>"
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().drafts().create(userId="me", body={"message": {"raw": raw}}).execute()


# ---------------------------------------------------------------------------
# Google Sheets
# ---------------------------------------------------------------------------

def load_sheet_index(sheets_service) -> tuple[dict, int, int]:
    """
    Returns (email_to_row, stage_col_idx, last_contacted_col_idx).
    email_to_row maps email.lower() -> 1-based row number in the sheet.
    col indices are 1-based.
    """
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=config.SPREADSHEET_ID,
        range="1:1",
    ).execute()
    header = [h.strip() for h in result.get("values", [[]])[0]]

    def col_idx(name):
        try:
            return header.index(name) + 1  # 1-based
        except ValueError:
            return None

    email_col    = col_idx("Email")
    stage_col    = col_idx("Stage")
    contacted_col = col_idx("Last Contacted")

    if email_col is None:
        log.error("Sheet header missing 'Email' column - cannot update sheet")
        return {}, None, None

    # Read just the email column to build row index
    col_letter = _col_to_letter(email_col)
    email_result = sheets_service.spreadsheets().values().get(
        spreadsheetId=config.SPREADSHEET_ID,
        range=f"{col_letter}:{col_letter}",
    ).execute()

    email_to_row = {}
    for i, row in enumerate(email_result.get("values", []), start=1):
        if i == 1:
            continue  # skip header
        if row:
            email_to_row[row[0].strip().lower()] = i

    return email_to_row, stage_col, contacted_col


def _col_to_letter(n: int) -> str:
    result = ""
    while n > 0:
        n, rem = divmod(n - 1, 26)
        result = chr(65 + rem) + result
    return result


def update_sheet_row(sheets_service, row_num: int, touch: int, stage_col: int, contacted_col: int):
    today = date.today().isoformat()
    stage = f"Touch {touch} Drafted"
    updates = []
    if stage_col:
        updates.append({
            "range": f"{_col_to_letter(stage_col)}{row_num}",
            "values": [[stage]],
        })
    if contacted_col:
        updates.append({
            "range": f"{_col_to_letter(contacted_col)}{row_num}",
            "values": [[today]],
        })
    if updates:
        sheets_service.spreadsheets().values().batchUpdate(
            spreadsheetId=config.SPREADSHEET_ID,
            body={"valueInputOption": "USER_ENTERED", "data": updates},
        ).execute()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def determine_touch(email: str, send_log: dict) -> int | None:
    history = send_log.get(email.lower(), {})
    today = date.today()
    if 1 not in history:
        return 1
    t1_date = history[1]
    if 2 not in history:
        return 2 if (today - t1_date).days >= config.TOUCH_2_DELAY_DAYS else None
    t2_date = history[2]
    if 3 not in history:
        return 3 if (today - t2_date).days >= config.TOUCH_3_DELAY_DAYS else None
    return None


def run():
    creds          = get_credentials()
    gmail_service  = build("gmail", "v1", credentials=creds)
    sheets_service = build("sheets", "v4", credentials=creds)
    send_log       = load_send_log()

    signature_html = get_gmail_signature(gmail_service)
    log.info(f"Fetched Gmail signature ({len(signature_html)} chars)")

    email_to_row, stage_col, contacted_col = load_sheet_index(sheets_service)

    leads_path = Path(config.LEADS_FILE)
    if not leads_path.exists():
        log.error(f"Lead file not found: {leads_path}")
        return

    with open(leads_path, newline="", encoding="utf-8-sig") as f:
        raw_leads = list(csv.DictReader(f))[BATCH_START:BATCH_END]

    drafted = 0
    skipped = 0

    for lead in raw_leads:
        email = lead.get("Email", "").strip()
        if not email:
            continue

        touch = determine_touch(email, send_log)
        if touch is None:
            skipped += 1
            continue

        first_name   = lead.get("First Name", "").strip()
        ai_brand_fit = generate_ai_brand_fit(lead)

        lead["first_name"]   = first_name
        lead["ai_brand_fit"] = ai_brand_fit

        try:
            tmpl             = load_template(touch)
            subject, body_html = render_html(tmpl["body"], tmpl["subject"], lead, signature_html)
            create_draft(gmail_service, email, subject, body_html)
            append_send_log(email, touch, date.today())

            row_num = email_to_row.get(email.lower())
            if row_num:
                update_sheet_row(sheets_service, row_num, touch, stage_col, contacted_col)
                log.info(f"Drafted Touch {touch} -> {first_name} <{email}> | Sheet row {row_num} updated")
            else:
                log.warning(f"Drafted Touch {touch} -> {first_name} <{email}> | NOT found in sheet")

            drafted += 1
            time.sleep(0.5)
        except Exception as e:
            log.error(f"Failed {email}: {e}")

        if drafted >= BATCH_SIZE:
            break

    log.info(f"Done. Drafted: {drafted} | Skipped: {skipped}")


if __name__ == "__main__":
    run()
