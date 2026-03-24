# Outreach Automation Template — Nest Navigate

> Portable blueprint for the Nest Navigate B2B email outreach system.
> Paste into a new Claude Code session to rebuild the full system instantly.

---

## Brand Identity

**Brand Name:** Nest Navigate
**Sender Name:** Ryan Sito
**Sender Title:** Founder
**Sender Email:** ryan@nestnavigate.com
**Website:** https://nestnavigate.com
**Calendar/CTA Link:** [UPDATE: your Calendly or booking link]

**Value Proposition:**
Nest Navigate educates and supports first-time homebuyers through one of life's most stressful milestones, while helping brands show up at key moments to build trust and drive high-intent customer acquisition.

**Target Audience (B2B):**
Brands, franchise owners, and enterprise companies that want to reach high-intent first-time homebuyers *before and during* the homebuying journey:
- Home services, inspection, moving, cleaning, insurance, warranties
- Retail, furniture, appliances, home improvement
- Financial services, mortgage, banking, credit
- Lifestyle and wellness brands tied to stressful life transitions
- Franchise owners focused on local customer acquisition

**Tone:** Direct, credible, and concise — peer-to-peer, not salesy. Respect their time.

**Core Positioning:**
Nest Navigate bridges the gap between:
- Consumers navigating the stress and complexity of buying their first home
- Brands that can support, simplify, and add value during that journey

This creates timely, milestone-based engagement — more meaningful brand interactions rooted in trust, not interruption.

---

## Lead List

**File:** `leads/leads.csv`

**Expected CSV Columns:**
- `first_name` — contact's first name
- `last_name` — contact's last name
- `email` — primary business email
- `company` — brand or franchise name (used in personalization)
- `title` — contact's role (optional, for context)
- `industry` — sector/category (optional)
- `status` — workflow status (default: `new`)

---

## Email Sequence

### Touch 1 — Day 0 (Initial Outreach)

**Subject:** Unlock partnership + visibility with first-time homebuyers | Nest Navigate

```
Hi {{first_name}},

First-time homebuyers are one of the most high-intent consumer segments out there —
yet most brands miss them entirely because they show up too late, after the decision
is already made.

Nest Navigate changes that.

We educate and support first-time homebuyers through one of life's most stressful
milestones — and we bring brand partners in at the right moments along the way.
Instead of interrupting people after the fact, you show up when they actually need
you: before they sign, before they move in, before they choose who to trust.

For brands in home services, financial services, retail, and beyond, that means:
- High-intent leads at the start of the homebuying journey, not the end
- Milestone-based touchpoints that feel helpful, not intrusive
- A built-in trust signal from a platform they already rely on

If {{company}} is focused on acquiring customers earlier in the funnel — and building
real relationships with them — this could be a strong fit.

Worth a 20-minute call to see if the timing's right?

[BOOKING_LINK]

[SIGNATURE]
```

---

### Touch 2 — Day 3 (Follow-Up)

**Subject:** Re: Unlock partnership + visibility with first-time homebuyers | Nest Navigate

```
Hi {{first_name}},

Wanted to resurface this in case it got buried.

The short version: buying a first home is one of the most stressful, expensive,
confusing things a person does — and it creates a window where consumers are actively
looking for brands they can trust across home services, insurance, financial products,
furniture, you name it.

Nest Navigate sits at that window. We guide first-time buyers through the process and
introduce brand partners at the moments that actually matter.

For {{company}}, that could mean reaching a warm, high-intent audience at the exact
point they're making buying decisions — before your competitors are even in the picture.

Happy to walk you through how it works. 20 minutes, no pressure.

[BOOKING_LINK]

[SIGNATURE]
```

---

### Touch 3 — Day 7 (Final Touch)

**Subject:** Last note — first-time homebuyer partnerships | Nest Navigate

```
Hi {{first_name}},

I'll keep this short — I've reached out a couple times about connecting {{company}}
with high-intent first-time homebuyers at key moments in their journey.

If the timing isn't right, no worries at all. But if customer acquisition earlier in
the funnel is something on your radar this year, I'd love to show you what we're building.

Is this something worth 20 minutes?

[BOOKING_LINK]

[SIGNATURE]
```

---

## Sequence Timing

| Touch | Send Day | Condition |
|-------|----------|-----------|
| Touch 1 | Day 0 | All `status = new` leads |
| Touch 2 | Day 3 | No reply to Touch 1 |
| Touch 3 | Day 7 | No reply to Touch 2 |

---

## System Configuration

**Gmail / Google Workspace Account:** ryan@nestnavigate.com
**Google OAuth Credentials:** `credentials/credentials.json`
**Scheduled Send Time:** 9:00 AM weekdays

---

## Merge Field Reference

| Template Tag | CSV Column | Example |
|---|---|---|
| `{{first_name}}` | `first_name` | Jane |
| `{{last_name}}` | `last_name` | Smith |
| `{{company}}` | `company` | Acme Home Services |
| `{{title}}` | `title` | VP of Marketing |
| `{{sender_name}}` | config | Ryan Sito |
| `{{booking_link}}` | config | calendly.com/... |
| `{{signature}}` | config | full email signature block |

---

## Activation

1. Drop this file + `leads/leads.csv` into a new Claude Code project
2. Say: *"Use this template to rebuild the Nest Navigate outreach system"*
3. Claude Code generates: scripts, final email copy, scheduler, send logs
