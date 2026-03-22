# Nest Navigate Outreach - Project Reference

## What This Does
Reads leads from `leads/leads.csv`, generates a 1-sentence AI brand fit per lead using Claude, creates HTML Gmail drafts, and updates the Partner Tracker Google Sheet.

## Key Files
- `send_emails.py` - main script
- `config.py` - all config (sender info, file paths, API scopes, spreadsheet ID)
- `templates_v2/touch1.txt` - email template for Touch 1
- `leads/leads.csv` - Apollo export, ~494 leads
- `logs/send_log.csv` - tracks which leads have been drafted and when (auto-created)
- `credentials/credentials.json` - Google OAuth client secrets
- `credentials/token.json` - Google OAuth token (auto-created on first run, auto-deleted if scopes change)

## Google Sheet
- **Name:** Partner Tracker
- **Spreadsheet ID:** `1HuPcMhXKDzH2ikpQeZP6LFGt_aL63UtuOBsoQGx37HI`
- **URL:** https://docs.google.com/spreadsheets/d/1HuPcMhXKDzH2ikpQeZP6LFGt_aL63UtuOBsoQGx37HI/edit
- **Columns:** A=first_name, B=email, C=ai_brand_fit, G=status
- **Status written to column G** after drafting (e.g. "Touch 1 Drafted - 2026-03-22")

## Gmail Signature
Pulled live from Gmail settings via `users().settings().sendAs().list()` at runtime - no hardcoding. Requires `gmail.settings.basic` scope.

## API Scopes Required
```python
GMAIL_SCOPES = [
    "https://www.googleapis.com/auth/gmail.compose",
    "https://www.googleapis.com/auth/gmail.settings.basic",
    "https://www.googleapis.com/auth/spreadsheets",
]
```
Script auto-detects stale tokens and forces re-auth when scopes change.

## Batch Config (in send_emails.py)
```python
BATCH_START = 150   # 0-indexed slice of leads.csv (rows 151-200)
BATCH_END   = 200
BATCH_SIZE  = 50
```

## Sender Info (config.py)
- Name: Ryan Ramirez
- Title: Head of Rewards
- Email: ryan@nestnavigate.com
- Calendly: https://calendly.com/nestnavigate

## Touch Sequence Timing (config.py)
- Touch 2: 3 days after Touch 1
- Touch 3: 7 days after Touch 2

## Running
```powershell
python send_emails.py
```
First run opens browser for Google OAuth. Subsequent runs are silent unless token is stale.

## Claude API Key
Stored in `Claude NN Key.txt` in the project root.

## Common Issues
- **"Skipped: 50 / Drafted: 0"** - send_log.csv already has these leads. Delete `logs/send_log.csv` to reprocess.
- **403 insufficientPermissions** - delete `credentials/token.json` and rerun to force re-auth (script now does this automatically).
- **Sheet range error** - sheet is named "Partner Tracker", not "Sheet1".
