# New Campaign Setup Sheet

Fill this out and paste it to Claude. Everything below is what's needed to spin up a new campaign.

---

## 1. Client / Company Info
- **Company name:**
- **What they do (2-3 sentences):**
- **What they're offering partners (the hook):**
  - e.g. "We pre-buy $250 in gift cards from partner locations upfront"
- **Target customer moment** (what life event makes someone need this):
  - e.g. "buying their first home"

## 2. Gmail Account
- **Send-from email:**
- **Sender name:**
- **Sender title:**
- **credentials.json location on my machine:**
  - e.g. `C:\Users\ryans\Documents\client-x\credentials.json`

## 3. Anthropic API Key
- **Key:** `sk-ant-...`
  - (or say "same key as Nest Navigate")

## 4. Lead List
- **File path:**
  - e.g. `C:\Users\ryans\Documents\client-x\leads.csv`
- **Column name for first name:**
- **Column name for company name:**
- **Column name for email:**
- **Column name for industry:**
- **Column name for keywords/description:**
- **Starting row (how many leads already sent):**
  - e.g. `0` for a fresh list

## 5. Email Template
- **Subject line:**
- **Body:**
  ```
  Hi [first name],

  [Your opening line / pitch paragraph]

  [Second paragraph - what you're offering]

  [CTA]

  Best,
  [Sender name]
  ```
  (write it out — Claude will insert the brand-fit sentence automatically)

## 6. Brand-Fit Sentence Instructions
What should Claude write to connect each business to your client's platform?
- **Instruction:**
  - e.g. "Write 1 sentence explaining why this business is a natural fit for first-time homebuyers and our rewards network. Be specific to their product. No fluff."

## 7. Batch Size
- **Leads per run:**
  - e.g. `100`

---

## Example (Nest Navigate)
- **Company:** Nest Navigate
- **What they do:** Platform that guides first-time homebuyers through the homebuying journey using milestone-based education and rewards
- **Hook:** Pre-buy $250 in gift cards from partner locations upfront, no cost to join
- **Target moment:** Buying a first home
- **Send-from:** ryan@nestnavigate.com / Ryan Ramirez / Head of Rewards
- **credentials.json:** `credentials\credentials.json`
- **API key:** same key
- **Lead list:** `leads/Nest Navigate 1k Lead List v1.csv`
- **Columns:** First Name, Company Name for Emails, Email, Industry, Keywords
- **Starting row:** 300
- **Batch size:** 100
