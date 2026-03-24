# Activation Checklist — Nest Navigate Outreach System

Use this checklist every time you spin up the outreach system for a new lead batch.

---

## Pre-Launch Setup (Do Once)

- [ ] **Gmail account ready** — the sending address is set up and accessible
- [ ] **Google OAuth configured** — `credentials/credentials.json` in place (see Step 1 below)
- [ ] **Lead CSV formatted** — columns match merge field reference in `OUTREACH_TEMPLATE.md`
- [ ] **Brand details filled in** — all `[PLACEHOLDERS]` in `OUTREACH_TEMPLATE.md` are replaced
- [ ] **CTA link confirmed** — booking link / landing page is live and tested
- [ ] **Email copy reviewed** — all three touches proofread and approved

---

## Step 1 — Gmail API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable the **Gmail API**
4. Create **OAuth 2.0 credentials** → Desktop App
5. Download as `credentials.json`
6. Place in: `credentials/credentials.json`
7. First run will open a browser for auth — complete it once to generate `token.json`

---

## Step 2 — Prepare Your Lead List

1. Export leads to CSV with these minimum columns:
   - `first_name`, `email`
   - Optional: `last_name`, `company`, `city`/`market`
2. Remove duplicates and invalid emails
3. Save as: `leads/leads.csv`
4. Verify column headers match merge fields in the email templates

---

## Step 3 — Configure the System

1. Open `config.py` (or `.env` file, depending on setup)
2. Set:
   - `SENDER_EMAIL` = your Gmail address
   - `SENDER_NAME` = your display name
   - `BOOKING_LINK` = your CTA URL
   - `SEND_TIME` = preferred send window (e.g. `09:00 America/Chicago`)
3. Review `sequence.json` — confirm day intervals match your strategy

---

## Step 4 — Test Before Launch

- [ ] Send Touch 1 to yourself (test address) — verify formatting, links, merge fields
- [ ] Send Touch 2 to yourself — verify subject line threading works
- [ ] Send Touch 3 to yourself — check final CTA
- [ ] Confirm unsubscribe/opt-out handling works
- [ ] Check `logs/send_log.csv` is being written correctly

---

## Step 5 — Launch

- [ ] Set scheduler to run daily (cron job or Task Scheduler)
- [ ] Send Touch 1 to full lead list
- [ ] Monitor `logs/send_log.csv` for delivery status
- [ ] Check replies in Gmail — respond manually or route to CRM

---

## Step 6 — Ongoing Management

- [ ] **Daily:** Review replies, update lead statuses in `leads/leads.csv`
- [ ] **After each touch:** Mark replied/unsubscribed leads as `status = done` in CSV
- [ ] **New batch:** Drop new `leads.csv` → system picks up only leads without Touch 1 sent
- [ ] **Pause sequence:** Set `status = paused` for any lead to skip future touches

---

## Lead Status Reference

| Status Value | Meaning |
|---|---|
| `new` | Not yet contacted |
| `t1_sent` | Touch 1 sent, awaiting reply |
| `t2_sent` | Touch 2 sent, awaiting reply |
| `t3_sent` | Touch 3 sent — sequence complete |
| `replied` | Lead responded — handle manually |
| `unsubscribed` | Remove from all future sends |
| `paused` | Skip until manually re-activated |
| `done` | Sequence complete, no further action |

---

## File Structure

```
Nest-Navigate-Outreach/
├── OUTREACH_TEMPLATE.md      ← brand blueprint (this system)
├── ACTIVATION_CHECKLIST.md   ← this file
├── config.py                 ← sender info, timing settings
├── send_emails.py            ← main send script
├── scheduler.py              ← daily automation runner
├── leads/
│   └── leads.csv             ← your lead list (drop new batches here)
├── credentials/
│   ├── credentials.json      ← Gmail OAuth (never commit this)
│   └── token.json            ← auto-generated after first auth
├── logs/
│   └── send_log.csv          ← record of all sends
└── templates/
    ├── touch1.txt
    ├── touch2.txt
    └── touch3.txt
```

---

## Troubleshooting

| Issue | Fix |
|---|---|
| Auth error on first run | Delete `token.json` and re-authenticate |
| Merge fields showing `{{first_name}}` literally | Check CSV column header spelling |
| Emails going to spam | Warm up sending domain, check SPF/DKIM |
| Duplicate sends | Check `send_log.csv` for lead before adding to new batch |
| Scheduler not running | Verify cron job / Task Scheduler is active |
