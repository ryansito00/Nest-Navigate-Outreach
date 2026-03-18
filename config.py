"""
Nest Navigate Outreach — Configuration
Update these values before running the system.
"""

# Sender identity
SENDER_NAME = "YOUR_NAME"
SENDER_TITLE = "YOUR_TITLE"
SENDER_EMAIL = "your@gmail.com"
WEBSITE_URL = "https://nestnavigate.com"
BOOKING_LINK = "https://calendly.com/your-link"

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
