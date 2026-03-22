"""
Nest Navigate Outreach — Configuration
Update these values before running the system.
"""

# Sender identity
SENDER_NAME = "Ryan"                            # UPDATE: your first name or full name
SENDER_TITLE = "Founder"                        # UPDATE: your title
SENDER_EMAIL = "ryan@nestnavigate.com"          # UPDATE: your Nest Navigate email
WEBSITE_URL = "https://nestnavigate.com"
BOOKING_LINK = "https://calendly.com/nestnavigate"  # UPDATE: your booking link

# Email signature — appended via {{signature}} tag in templates (optional)
# UPDATE: paste your full signature here, use \n for line breaks
EMAIL_SIGNATURE = """Ryan
Founder | Nest Navigate
ryan@nestnavigate.com
nestnavigate.com"""

# File paths
LEADS_FILE = "leads/leads.csv"
SEND_LOG_FILE = "logs/send_log.csv"
CREDENTIALS_FILE = "credentials/credentials.json"
TOKEN_FILE = "credentials/token.json"
TEMPLATES_DIR = "templates"

# Sequence timing (days after Touch 1)
TOUCH_2_DELAY_DAYS = 3
TOUCH_3_DELAY_DAYS = 7

# Send window — emails only go out during these hours (local time)
SEND_HOUR_START = 9   # 9 AM
SEND_HOUR_END = 17    # 5 PM
SEND_WEEKDAYS_ONLY = True

# Gmail API scope
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
