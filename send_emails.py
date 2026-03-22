"""
Nest Navigate Outreach — Email Sender
Reads leads.csv, checks send_log.csv, and sends the appropriate touch.
"""

import csv
import os
import base64
import json
import logging
from datetime import datetime, date, timedelta
from email.mime.text import MIMEText
from pathlib import Path

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


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def get_gmail_service():
    creds = None
    token_path = config.TOKEN_FILE
    creds_path = config.CREDENTIALS_FILE

    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, config.GMAIL_SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, config.GMAIL_SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w") as f:
            f.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

def load_template(touch_number: int) -> dict:
    """Load subject and body from templates/touch{N}.txt"""
    path = Path(config.TEMPLATES_DIR) / f"touch{touch_number}.txt"
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {path}")

    content = path.read_text()
    lines = content.strip().splitlines()

    subject_line = next((l for l in lines if l.lower().startswith("subject:")), None)
    if not subject_line:
        raise ValueError(f"No 'Subject:' line found in {path}")

    subject = subject_line.split(":", 1)[1].strip()
    # Body is everything after the subject line + blank line
    subject_idx = lines.index(subject_line)
    body = "\n".join(lines[subject_idx + 2:]).strip()

    return {"subject": subject, "body": body}


def render(template: str, lead: dict) -> str:
    """Replace {{field}} placeholders with lead data."""
    for key, value in lead.items():
        template = template.replace(f"{{{{{key}}}}}", value or "")
    # Also inject config values
    replacements = {
        "{{sender_name}}": config.SENDER_NAME,
        "{{sender_title}}": config.SENDER_TITLE,
        "{{website}}": config.WEBSITE_URL,
        "{{signature}}": config.EMAIL_SIGNATURE,
    }
    for tag, value in replacements.items():
        template = template.replace(tag, value)
    return template


# ---------------------------------------------------------------------------
# Send log
# ---------------------------------------------------------------------------

def load_send_log() -> dict:
    """Returns dict keyed by email -> {touch: date_sent}"""
    log_data = {}
    path = Path(config.SEND_LOG_FILE)
    if not path.exists():
        return log_data

    with open(path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            email = row["email"].lower()
            if email not in log_data:
                log_data[email] = {}
            log_data[email][int(row["touch"])] = datetime.strptime(row["sent_date"], "%Y-%m-%d").date()

    return log_data


def append_send_log(email: str, touch: int, sent_date: date):
    path = Path(config.SEND_LOG_FILE)
    write_header = not path.exists() or path.stat().st_size == 0

    with open(path, "a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["email", "touch", "sent_date"])
        writer.writerow([email.lower(), touch, sent_date.isoformat()])


# ---------------------------------------------------------------------------
# Gmail send
# ---------------------------------------------------------------------------

def send_email(service, to: str, subject: str, body: str):
    message = MIMEText(body, "plain")
    message["to"] = to
    message["from"] = f"{config.SENDER_NAME} <{config.SENDER_EMAIL}>"
    message["subject"] = subject

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().drafts().create(userId="me", body={"message": {"raw": raw}}).execute()


# ---------------------------------------------------------------------------
# Main logic
# ---------------------------------------------------------------------------

def determine_touch(email: str, send_log: dict) -> int | None:
    """Return which touch to send next, or None if sequence is complete."""
    history = send_log.get(email.lower(), {})
    today = date.today()

    if 1 not in history:
        return 1

    t1_date = history[1]
    if 2 not in history:
        if (today - t1_date).days >= config.TOUCH_2_DELAY_DAYS:
            return 2
        return None

    t2_date = history[2]
    if 3 not in history:
        if (today - t2_date).days >= config.TOUCH_3_DELAY_DAYS:
            return 3
        return None

    return None  # Sequence complete


def is_within_send_window() -> bool:
    now = datetime.now()
    if config.SEND_WEEKDAYS_ONLY and now.weekday() >= 5:
        return False
    return config.SEND_HOUR_START <= now.hour < config.SEND_HOUR_END


def run():
    if not is_within_send_window():
        log.info("Outside send window — exiting.")
        return

    service = get_gmail_service()
    send_log = load_send_log()

    leads_path = Path(config.LEADS_FILE)
    if not leads_path.exists():
        log.error(f"Lead file not found: {leads_path}")
        return

    # Normalize Apollo export column names to internal keys
    COLUMN_MAP = {
        "First Name": "first_name",
        "Last Name": "last_name",
        "Email": "email",
        "Company Name for Emails": "company",
        "Title": "title",
        "Industry": "industry",
    }

    with open(leads_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        raw_leads = list(reader)[150:200]

    leads = []
    for row in raw_leads:
        normalized = {COLUMN_MAP.get(k, k): v for k, v in row.items()}
        leads.append(normalized)

    sent_count = 0
    skip_count = 0

    for lead in leads[BATCH_START:BATCH_END]:
        email = lead.get("email", "").strip()
        status = lead.get("status", "new").strip().lower()

        if not email:
            continue
        if status in ("replied", "unsubscribed", "done", "paused"):
            skip_count += 1
            continue

        touch = determine_touch(email, send_log)
        if touch is None:
            skip_count += 1
            continue

        try:
            tmpl = load_template(touch)
            subject = render(tmpl["subject"], lead)
            body = render(tmpl["body"], lead)
            send_email(service, email, subject, body)
            append_send_log(email, touch, date.today())
            log.info(f"Sent Touch {touch} → {email}")
            sent_count += 1
        except Exception as e:
            log.error(f"Failed to send Touch {touch} to {email}: {e}")

    log.info(f"Done. Sent: {sent_count} | Skipped: {skip_count}")


if __name__ == "__main__":
    run()




