"""
Nest Navigate — Daily Draft Creator
Processes BATCH_SIZE leads per run, saves progress, creates Gmail drafts.
Usage:
  python create_drafts.py
"""

import csv
import json
import base64
import os
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import anthropic

# ── Config ─────────────────────────────────────────────────────────────────────
CLAUDE_API_KEY = "PASTE_CLAUDE_KEY_HERE"
LEADS_FILE     = "leads/Nest Navigate 1k Lead List v1.csv"
PROGRESS_FILE  = "leads/progress.json"
CREDENTIALS    = "credentials.json"
TOKEN_FILE     = "token.json"
BATCH_SIZE     = 100
SCOPES         = [
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.settings.basic",
]

# ── Nest Navigate system context ───────────────────────────────────────────────
NN_SYSTEM = """
You are a partnership outreach specialist for Nest Navigate.
Nest Navigate is a platform that guides first-time homebuyers through the homebuying
journey using milestone-based education and rewards. As users complete educational
milestones — getting pre-approved, understanding closing costs, making their first
offer — they earn rewards redeemable at select local business partners.

Nest Navigate pre-buys $250 in gift cards from partner locations upfront. There is
no cost for partners to join. Partners get visibility on the platform and in
milestone completion emails sent to motivated first-time homebuyers.

Your job is to write a single, highly specific sentence explaining why a particular
business is a natural fit for first-time homebuyers and the Nest Navigate rewards
network. Be concrete, not generic. Connect the company's actual product or service
to the moment of buying a first home.
"""

# ── Progress tracking ──────────────────────────────────────────────────────────
def load_progress() -> dict:
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {"last_row": 150}  # First 150 already sent

def save_progress(row_index: int):
    with open(PROGRESS_FILE, "w") as f:
        json.dump({"last_row": row_index}, f)

# ── Claude: generate brand-fit sentence ───────────────────────────────────────
def generate_brand_fit(row: dict) -> str:
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

    company  = row.get("Company Name for Emails", "").strip()
    industry = row.get("Industry", "").strip()
    keywords = row.get("Keywords", "").strip()
    keywords = keywords[:600] if len(keywords) > 600 else keywords

    prompt = f"""
Write EXACTLY 1 sentence (no more) explaining why {company} is a natural fit for
first-time homebuyers and the Nest Navigate rewards network.

Company: {company}
Industry: {industry}
Keywords: {keywords}

Rules:
- 1 sentence only
- Be specific to this company's actual product/service
- Connect it directly to the first-time homebuyer moment
- No fluff, no filler
- Do NOT start with "I" or "Nest Navigate"
"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=150,
        system=NN_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()

# ── Gmail ──────────────────────────────────────────────────────────────────────
def authenticate():
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return creds

def get_gmail_signature(service) -> str:
    try:
        result = service.users().settings().sendAs().list(userId="me").execute()
        for send_as in result.get("sendAs", []):
            if send_as.get("isPrimary"):
                return send_as.get("signature", "")
    except Exception as e:
        print(f"  [could not fetch signature: {e}]")
    return ""

def _build_html(plain_body: str, signature_html: str) -> str:
    html = plain_body.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    html = html.replace("\n", "<br>\n")
    return f"<div>{html}</div><br>{signature_html}"

def create_draft(service, to_email: str, subject: str, plain_body: str, signature_html: str):
    msg = MIMEMultipart("alternative")
    msg["to"] = to_email
    msg["subject"] = subject
    msg.attach(MIMEText(plain_body, "plain"))
    msg.attach(MIMEText(_build_html(plain_body, signature_html), "html"))
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().drafts().create(
        userId="me", body={"message": {"raw": raw}}
    ).execute()

# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    progress  = load_progress()
    start_row = progress["last_row"]

    with open(LEADS_FILE, newline="", encoding="utf-8-sig") as f:
        all_rows = list(csv.DictReader(f))

    total = len(all_rows)
    if start_row >= total:
        print("All leads processed. Reset progress.json to start over.")
        return

    batch = all_rows[start_row : start_row + BATCH_SIZE]
    remaining_after = max(0, total - start_row - len(batch))

    print(f"Today: rows {start_row + 1}–{start_row + len(batch)} of {total}")
    print(f"Remaining after today: {remaining_after}\n")

    creds   = authenticate()
    service = build("gmail", "v1", credentials=creds)

    signature_html = get_gmail_signature(service)
    print(f"  [Signature fetched: {len(signature_html)} chars]\n")

    drafted = 0
    skipped = 0
    errors  = 0

    for i, row in enumerate(batch):
        abs_row = start_row + i
        email   = row.get("Email", "").strip()
        fname   = row.get("First Name", "there").strip()
        company = row.get("Company Name for Emails", "").strip()

        if not email:
            print(f"  [{i+1}/{len(batch)}] SKIP (no email): {fname} @ {company}")
            save_progress(abs_row + 1)
            skipped += 1
            continue

        print(f"  [{i+1}/{len(batch)}] {fname} @ {company} — {row.get('Title', '')}")

        try:
            brand_fit = generate_brand_fit(row)
        except Exception as e:
            print(f"    ERROR generating brand fit: {e}")
            save_progress(abs_row + 1)
            errors += 1
            continue

        subject = "Can we pre-buy $250 in gift cards from your location?"
        body = f"""Hi {fname},

I lead the Rewards program for Nest Navigate, a platform that guides first-time homebuyers through the homebuying journey using milestone-based education and rewards.

As users complete educational milestones on our platform, they earn rewards redeemable at select local partners. No cost for you to join. We're just looking for partners that want visibility on our platform and align with supporting first-time homebuyers. {brand_fit}

We'd start by pre-buying $250 in gift cards from your location and promoting your brand on our site immediately. If our users are choosing your brand frequently, we'd be very open to making a more in-depth partnership.

Would love to hop on a call if this sounds interesting.

Best,
Ryan"""

        try:
            create_draft(service, email, subject, body, signature_html)
            drafted += 1
            save_progress(abs_row + 1)
            print(f"    ✓ Draft created")
        except Exception as e:
            print(f"    ERROR creating draft: {e}")
            errors += 1

        time.sleep(0.75)

    print(f"\n── Summary ──────────────────────────────────")
    print(f"  Drafted:  {drafted}")
    print(f"  Skipped:  {skipped}")
    print(f"  Errors:   {errors}")
    print(f"  Progress: row {start_row + len(batch)} of {total}")
    print(f"  Run again tomorrow for the next {BATCH_SIZE}.")

if __name__ == "__main__":
    main()
