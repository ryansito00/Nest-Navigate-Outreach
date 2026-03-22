"""
Nest Navigate Outreach - Email Drafter
Reads leads.csv rows 151-200, generates AI brand fit, creates Gmail drafts.
"""

import csv
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

# Load Claude API key
_key_path = Path("Claude NN Key.txt")
CLAUDE_API_KEY = _key_path.read_text().strip() if _key_path.exists() else os.environ.get("ANTHROPIC_API_KEY", "")


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

def get_gmail_service():
    creds = None
    if os.path.exists(config.TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(config.TOKEN_FILE, config.GMAIL_SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(config.CREDENTIALS_FILE, config.GMAIL_SCOPES)
            creds = flow.run_local_server(port=0)
        with open(config.TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


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
- Do not start with "I" or mention Nest Navigate"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=100,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


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


def render(template: str, lead: dict) -> str:
    for key, value in lead.items():
        template = template.replace(f"{{{{{key}}}}}", str(value) if value else "")
    template = template.replace("{{signature}}", config.EMAIL_SIGNATURE)
    template = template.replace("{{sender_name}}", config.SENDER_NAME)
    template = template.replace("{{sender_title}}", config.SENDER_TITLE)
    template = template.replace("{{website}}", config.WEBSITE_URL)
    return template


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

def create_draft(service, to: str, subject: str, body: str):
    message = MIMEText(body, "plain")
    message["to"]      = to
    message["from"]    = f"{config.SENDER_NAME} <{config.SENDER_EMAIL}>"
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    service.users().drafts().create(userId="me", body={"message": {"raw": raw}}).execute()


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
    service  = get_gmail_service()
    send_log = load_send_log()

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
            tmpl    = load_template(touch)
            subject = render(tmpl["subject"], lead)
            body    = render(tmpl["body"], lead)
            create_draft(service, email, subject, body)
            append_send_log(email, touch, date.today())
            log.info(f"Drafted Touch {touch} -> {first_name} <{email}>")
            drafted += 1
            time.sleep(0.5)
        except Exception as e:
            log.error(f"Failed {email}: {e}")

        if drafted >= BATCH_SIZE:
            break

    log.info(f"Done. Drafted: {drafted} | Skipped: {skipped}")


if __name__ == "__main__":
    run()
