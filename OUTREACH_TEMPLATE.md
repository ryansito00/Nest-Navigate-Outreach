# Outreach Automation Template — Nest Navigate

> This file is the portable blueprint for the Nest Navigate email outreach system.
> Paste this into a new Claude Code session along with brand/lead details to rebuild the full system instantly.

---

## Brand Identity

**Brand Name:** Nest Navigate
**Sender Name:** [SENDER_NAME]
**Sender Title:** [SENDER_TITLE]
**Sender Email:** [SENDER_EMAIL]
**Website:** [WEBSITE_URL]
**Calendar/CTA Link:** [BOOKING_LINK]

**Value Proposition:**
[One sentence — what does Nest Navigate do and who is it for?]

**Target Audience:**
[Who are these leads? E.g. homebuyers, real estate investors, agents, renters, etc.]

**Tone:** [E.g. warm and professional / direct and concise / conversational]

**Key Talking Points:**
1. [Point 1]
2. [Point 2]
3. [Point 3]

---

## Lead List

**File:** `leads/leads.csv`

**Expected CSV Columns:**
- `first_name` — lead's first name (used in personalization)
- `last_name` — lead's last name
- `email` — primary email address
- `company` — company or brokerage (if applicable)
- `city` or `market` — geographic market (if applicable)
- `[custom_field]` — any additional personalization fields

> Adjust merge fields in email templates below to match your actual CSV column headers.

---

## Email Sequence

### Touch 1 — Day 0 (Initial Outreach)

**Subject:** [SUBJECT_LINE_1]

```
Hi {{first_name}},

[OPENING — reference something relevant to them or their market]

[VALUE STATEMENT — what Nest Navigate does and why it matters to them]

[CTA — soft ask, low friction]

[SENDER_NAME]
[SENDER_TITLE] | Nest Navigate
[WEBSITE_URL]
```

---

### Touch 2 — Day 3 (Follow-Up)

**Subject:** Re: [SUBJECT_LINE_1]

```
Hi {{first_name}},

[BRIEF — acknowledge no response, not pushy]

[REFRAME VALUE — different angle or social proof]

[CTA — same or slightly different ask]

[SENDER_NAME]
```

---

### Touch 3 — Day 7 (Final Touch)

**Subject:** [SUBJECT_LINE_3]

```
Hi {{first_name}},

[SHORT — respect their time]

[SINGLE CLEAR ASK]

[SOFT CLOSE — leave door open]

[SENDER_NAME]
```

---

## Sequence Timing

| Touch | Send Day | Condition |
|-------|----------|-----------|
| Touch 1 | Day 0 | All new leads |
| Touch 2 | Day 3 | No reply to Touch 1 |
| Touch 3 | Day 7 | No reply to Touch 2 |

---

## System Configuration

**Gmail Account:** [GMAIL_ADDRESS]
**Google OAuth Credentials:** `credentials/credentials.json`
**Scheduled Send Time:** [HH:MM] [TIMEZONE] on weekdays

---

## Merge Field Reference

| Template Tag | CSV Column | Example |
|---|---|---|
| `{{first_name}}` | `first_name` | Sarah |
| `{{last_name}}` | `last_name` | Johnson |
| `{{company}}` | `company` | Keller Williams |
| `{{market}}` | `city` | Austin |

---

## Activation

Once brand details are filled in:

1. Drop this file + `leads/leads.csv` into a new Claude Code project
2. Say: *"Use this template to build the outreach system with these brand details: [paste details]"*
3. Claude Code will generate: scripts, final email copy, scheduler, send logs
