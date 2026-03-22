"""
Nest Navigate — Batch Draft Creator
Reads leads starting at BATCH_START_ROW, generates brand-fit sentences,
and creates Gmail drafts for each lead.
"""

import csv
import os
import base64
import logging
from email.mime.text import MIMEText
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

import config

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Batch settings
# ---------------------------------------------------------------------------

BATCH_START_ROW = 151   # 1-indexed, first lead to draft (skip already-sent leads)
BATCH_END_ROW   = None  # Set to a row number to stop early, or None for all remaining

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
            flow = InstalledAppFlow.from_client_secrets_file(
                config.CREDENTIALS_FILE,
                ["https://www.googleapis.com/auth/gmail.compose",
                 "https://www.googleapis.com/auth/gmail.send"]
            )
            creds = flow.run_local_server(port=0)
        with open(config.TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


# ---------------------------------------------------------------------------
# Brand-fit sentence generator
# ---------------------------------------------------------------------------

def brand_fit(company: str, industry: str, keywords: str) -> str:
    c = company.lower()
    k = keywords.lower()
    i = industry.lower()

    # Home inspection
    if any(x in c for x in ["pillar to post", "morrison property", "home inspector"]):
        return "Your customers are literally our users — first-time homebuyers need a home inspection to close, making this one of the most natural partnerships we could build."

    # Home restoration / damage
    if any(x in c for x in ["911 restoration", "servpro", "united water restoration", "all dry", "servicemaster"]):
        return "New homeowners will face their first water, fire, or mold issue sooner than they expect — getting your brand on their radar before that happens is genuinely valuable."

    # Home services / maintenance
    if any(x in c for x in ["homesmiles", "ace handyman", "fish window", "midtown chimney", "cleaning authority", "maidpro", "stratus", "iNX", "inx commercial", "painter bros", "garage force"]):
        return "First-time homeowners quickly realize how much upkeep a home requires — your services are exactly what they'll be looking for in those first few months."

    # Home improvement / tools
    if any(x in c for x in ["snap-on", "matco", "mac tools", "winzer", "batteries plus", "budget blinds", "floor coverings", "shelfgenie", "fastsigns", "seal methods"]):
        return "New homeowners are outfitting and maintaining their space for the first time — your products are a natural early purchase for buyers settling in."

    # Pool services
    if any(x in c for x in ["puddle pool", "california pools"]):
        return "First-time homeowners with a pool need reliable service fast — getting your name in front of them before they start searching is a real advantage."

    # Senior care (stretch fit, but worth trying)
    if any(x in c for x in ["home instead", "senior helpers", "seniors helping seniors", "firstlight", "griswold", "a place at home", "amada", "visiting angels", "home matters caregiving", "chefs for seniors"]):
        return "Many first-time homebuyers purchase with multi-generational living in mind — your services may be more relevant to our users than you'd expect."

    # Fitness / wellness
    if any(x in c for x in ["orangetheory", "hotworx", "f45", "bodyrok", "row house", "cyclebar", "body fit", "rumble boxing", "title boxing", "isi elite", "overtime athletics", "pvolve", "jazzercise", "bar method", "club pilates", "stretch", "perspire", "gameday men"]):
        return "The homebuying process is physically and emotionally draining — your studio is a great reward for buyers who are finally ready to breathe and invest in themselves."

    # Massage / spa / chiropractic
    if any(x in c for x in ["massage envy", "the now", "hand & stone", "massage heights", "the joint", "array skin", "face foundrié", "face foundrie", "european wax", "amazing lash", "hello sugar", "drybar", "hammer & nails", "alignmed"]):
        return "Homebuying is one of the most stressful experiences in a person's life — your services are a perfect reward for buyers who've earned a moment of self-care."

    # Swim schools
    if any(x in c for x in ["british swim school", "aqua-tots"]):
        return "First-time homebuying families immediately start looking for trusted community programs — swim school is one of the first things parents with young kids seek out in a new neighborhood."

    # Kids / education
    if any(x in c for x in ["kidspark", "mathnasium", "genius kids", "code ninjas", "learning experience", "children's music", "eye level", "tga premier", "i9 sports", "school of rock", "primrose"]):
        return "First-time homebuying families are immediately scouting enrichment and childcare options in their new neighborhood — your program is exactly what they'll be looking for."

    # Pet services
    if any(x in c for x in ["scenthound", "zoomin groomin", "pet butler"]):
        return "Many first-time homebuyers are pet owners finally settling into a home with more space — your services are a great early discovery for new homeowners with pets."

    # Hair / salon
    if any(x in c for x in ["sport clips", "great clips", "my salon suite", "sola salon"]):
        return "New homeowners are establishing routines in their new neighborhood — finding a go-to salon is one of the first things people do when they move somewhere new."

    # Food / beverage (celebratory)
    if any(x in c for x in ["nothing bundt", "baskin-robbins", "parlor doughnuts", "popbar", "yogurtland", "kona ice", "ubatuba", "rush bowls", "boba loca", "teaspoon", "graze craze", "mill creek bakery", "wetzel", "dutch bros"]):
        return "Closing on a first home is a milestone that deserves a celebration — your brand is a perfect fit for buyers looking for a local treat to mark the moment."

    # Quick service / casual dining
    if any(x in c for x in ["chick-fil-a", "firehouse subs", "shakey's", "little caesar", "popeyes", "arby's", "burger king", "jack in the box", "mcdonald's", "subway", "teriyaki madness", "baja fresh", "daphne's", "nekter", "7-eleven"]):
        return "First-time buyers are busy, tired, and moving — a gift card for a quick, familiar meal is a practical and genuinely appreciated reward during one of the most hectic weeks of their lives."

    # Travel / cruises
    if any(x in c for x in ["cruise planners", "dream vacations", "expedia cruise", "expedia cruises"]):
        return "Closing on a first home is one of the biggest milestones in a person's life — and a vacation is the natural next step for buyers finally ready to celebrate and exhale."

    # Financial
    if any(x in c for x in ["liberty tax", "h&r block", "ameriprise", "freeway insurance", "fiesta", "coversure", "market america"]):
        return "First-time homeowners are navigating new financial territory — your services are a timely and relevant resource for buyers at a major crossroads."

    # Shipping / business services
    if any(x in c for x in ["ups store", "postalannex", "unishippers", "inxpress", "fastsigns", "nerds", "safeguard", "electronic payments", "express services", "spherion"]):
        return "First-time homebuyers are often also small business owners managing a major life transition — your services are a practical and well-timed introduction."

    # Auto
    if any(x in c for x in ["toyota", "fix auto", "fast undercar", "hertz"]):
        return "New homeowners are making several major purchases at once — having your brand on their radar during the homebuying journey puts you ahead of competitors when they're ready to buy."

    # Retail / décor / estate sales
    if any(x in c for x in ["grasons", "blue moon estate", "kitsy lane", "big frog", "city lifestyle", "n2 company", "valpak", "money mailer"]):
        return "First-time homebuyers are outfitting and discovering their new community all at once — your brand is a natural fit for buyers ready to spend and explore."

    # Luxury / fashion (stretch, but present in list)
    if any(x in c for x in ["louis vuitton", "givenchy", "giorgio armani", "galia lahav", "estee lauder", "sephora"]):
        return "Buying a first home is one of the most significant milestones in a person's life — celebrating with a touch of luxury is a natural reward for buyers who've worked hard to get there."

    # Junk removal
    if "junkluggers" in c:
        return "Moving into a first home often means clearing out the old — The Junkluggers is a perfectly timed reward for buyers ready to start fresh."

    # Outdoor / sports / hobbies
    if any(x in c for x in ["outdoor connection", "rip curl", "destination athlete", "american poolplayers"]):
        return "New homeowners are ready to explore their community and lifestyle — your brand is a great fit for buyers eager to settle in and get active."

    # GNC / nutrition
    if "gnc" in c:
        return "First-time homeowners are building new routines from the ground up — GNC is a natural early stop for buyers investing in their health in a new neighborhood."

    # Tutoring / academics
    if any(x in c for x in ["juice plus", "mathnasium"]):
        return "Families buying their first home are actively setting up their kids for success in a new neighborhood — your programs are a great early introduction."

    # Cleaning / home care
    if any(x in c for x in ["maidpro", "cleaning authority"]):
        return "New homeowners quickly realize how much upkeep a home requires — a gift card for professional cleaning is one of the most practical rewards we can offer."

    # Fallback by industry
    if "real estate" in i:
        return "Our users are your future customers — first-time homebuyers who will need real estate services, referrals, and local expertise as they settle in."
    if "food" in i or "beverage" in i or "restaurant" in i:
        return "Closing day calls for a celebration, and first-time buyers are eager to discover their new neighborhood's best spots — your location is a great fit for that moment."
    if "fitness" in i or "wellness" in i or "health" in i:
        return "First-time homebuyers are stressed, exhausted, and ready to invest in themselves — your services are a natural reward for buyers who've made it to the finish line."
    if "retail" in i:
        return "First-time homeowners are active, local consumers in the middle of a major life transition — your brand is well-positioned to make a strong first impression."
    if "education" in i:
        return "First-time homebuying families are immediately scouting resources for their kids in their new neighborhood — your program is exactly what they'll be searching for."

    # Generic fallback
    return "We love connecting with local businesses that align with buyers at a major life milestone — your brand is a great fit for the community we're building."


# ---------------------------------------------------------------------------
# Template
# ---------------------------------------------------------------------------

SUBJECT = "Can we pre-buy $250 in gift cards from your location?"

BODY_TEMPLATE = """Hi {first_name},

I lead the Rewards program for Nest Navigate, a platform that guides first-time homebuyers through the homebuying journey using milestone-based education and rewards.

As users complete educational milestones on our platform, they earn rewards redeemable at select local partners. No cost for you to join. We're just looking for partners that want visibility on our platform and align with supporting first-time homebuyers. {ai_brand_fit}

We'd start by pre-buying $250 in gift cards from your location and promoting your brand on our site immediately. If our users are choosing your brand frequently, we'd be very open to making a more in-depth partnership.

Would love to hop on a call if this sounds interesting.

Best,
{signature}"""

SIGNATURE = """Ryan
Founder | Nest Navigate
ryan@nestnavigate.com
nestnavigate.com"""


# ---------------------------------------------------------------------------
# Draft creation
# ---------------------------------------------------------------------------

def create_draft(service, to: str, subject: str, body: str):
    message = MIMEText(body, "plain")
    message["to"] = to
    message["from"] = f"Ryan <{config.SENDER_EMAIL}>"
    message["subject"] = subject
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    draft = service.users().drafts().create(userId="me", body={"message": {"raw": raw}}).execute()
    return draft["id"]


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run():
    service = get_gmail_service()

    leads_path = Path(config.LEADS_FILE)
    with open(leads_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        all_rows = list(reader)

    start_idx = BATCH_START_ROW - 1  # convert to 0-indexed
    end_idx   = BATCH_END_ROW if BATCH_END_ROW else len(all_rows)
    batch     = all_rows[start_idx:end_idx]

    log.info(f"Creating drafts for rows {BATCH_START_ROW} to {end_idx} ({len(batch)} leads)")

    created = 0
    skipped = 0

    for row in batch:
        first_name = row.get("First Name", "").strip()
        email      = row.get("Email", "").strip()
        company    = row.get("Company Name for Emails", "").strip()
        industry   = row.get("Industry", "").strip()
        keywords   = row.get("Keywords", "").strip()

        if not email or not first_name:
            skipped += 1
            continue

        fit     = brand_fit(company, industry, keywords)
        body    = BODY_TEMPLATE.format(
            first_name=first_name,
            ai_brand_fit=fit,
            signature=SIGNATURE
        )

        try:
            draft_id = create_draft(service, email, SUBJECT, body)
            log.info(f"Draft created → {first_name} ({company}) [{email}] — {draft_id}")
            created += 1
        except Exception as e:
            log.error(f"Failed for {email}: {e}")
            skipped += 1

    log.info(f"Done. Drafts created: {created} | Skipped: {skipped}")


if __name__ == "__main__":
    run()
