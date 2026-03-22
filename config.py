"""
Nest Navigate Outreach - Configuration
"""

# Sender identity
SENDER_NAME = "Ryan Ramirez"
SENDER_TITLE = "Head of Rewards"
SENDER_EMAIL = "ryan@nestnavigate.com"
WEBSITE_URL = "https://nestnavigate.com"
BOOKING_LINK = "https://calendly.com/nestnavigate"

# Email signature - appended via {{signature}} tag in templates
EMAIL_SIGNATURE = """Ryan Ramirez
Head of Rewards
Nest Navigate | nestnavigate.com
m) 571-338-7022"""

# File paths
LEADS_FILE = "leads/leads.csv"
SEND_LOG_FILE = "logs/send_log.csv"
CREDENTIALS_FILE = "credentials/credentials.json"
TOKEN_FILE = "credentials/token.json"
TEMPLATES_DIR = "templates"

# Sequence timing (days after Touch 1)
TOUCH_2_DELAY_DAYS = 3
TOUCH_3_DELAY_DAYS = 7

# Send window - emails only go out during these hours (local time)
SEND_HOUR_START = 0   # 9 AM
SEND_HOUR_END = 24    # 5 PM
SEND_WEEKDAYS_ONLY = False

# Gmail API scope
GMAIL_SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]




