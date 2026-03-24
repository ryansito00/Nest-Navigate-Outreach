# Nest Navigate Outreach — Claude Memory

## What this project does
Python script (`create_drafts.py`) that processes 100 leads at a time from a CSV, generates a personalized brand-fit sentence via Claude AI, and creates Gmail drafts ready to send.

## Every time we run a new batch

1. Reset progress to the right row:
   ```
   echo {"last_row": 300} > leads\progress.json
   ```
   (change 300 to wherever you want to start)

2. Delete token.json if scopes changed:
   ```
   del token.json
   ```

3. Run:
   ```
   python create_drafts.py
   ```

## ANTHROPIC_API_KEY setup (Windows)
The API key is read from the environment variable `ANTHROPIC_API_KEY`.

- `setx` saves it permanently but requires opening a **new terminal** to take effect
- If the key isn't working, set it directly in the current terminal (no quotes, no spaces around `=`):
  ```
  set ANTHROPIC_API_KEY=sk-ant-yourkey
  ```
- Verify it's set: `echo %ANTHROPIC_API_KEY%`

## Gmail OAuth token.json
- `token.json` stores Gmail credentials. Delete it whenever scopes change or auth breaks.
- Current scopes needed:
  - `gmail.compose` — to create drafts
  - `gmail.settings.basic` — to fetch the HTML signature from sendAs

## Gmail signature
- Fetched live from Gmail settings via `get_gmail_signature(service)` → `users.settings().sendAs()`
- Returns the HTML signature from Ryan's primary send-as address
- Embedded into each draft as HTML using `EmailMessage.add_alternative`
- If you see `[Signature fetched: 0 chars]` → delete `token.json` and re-auth (scope issue)

## Lead file
- `leads/Nest Navigate 1k Lead List v1.csv` — 494 rows total
- Progress tracked in `leads/progress.json` → `{"last_row": N}`
- Batches 1–150: already sent before this script existed
- Batch 151–300: sent in earlier runs
- Batch 301–400: current target

## cd to project
```
cd "C:\Users\ryans\OneDrive\Desktop\Automated Outreach\Nest-Navigate-Outreach"
```

## Email writing rules
- NEVER use em dashes (—) in emails. Use a comma, period, or rewrite the sentence instead.

## Common errors and fixes

| Error | Fix |
|-------|-----|
| `Could not resolve authentication method` | `set ANTHROPIC_API_KEY=sk-ant-yourkey` (no quotes) |
| `Signature fetched: 0 chars` + 403 | `del token.json` then re-run |
| `All leads processed` | Reset `leads/progress.json` to correct row |
| `git pull` merge conflict | `git reset --hard origin/claude/launch-business-drafts-bjV03` then pull |
| Script runs from wrong folder | `cd` to project folder first |
