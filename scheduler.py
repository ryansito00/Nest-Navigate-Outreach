"""
Nest Navigate Outreach — Scheduler
Runs send_emails.py daily at the configured time.
Use this for automated daily sends, or just run send_emails.py directly.

Usage:
    python scheduler.py          # Runs continuously, sends daily at configured time
    python scheduler.py --now    # Force-run immediately (ignores time window)
"""

import sys
import time
import logging
import subprocess
from datetime import datetime

import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
log = logging.getLogger(__name__)


def run_send():
    log.info("Running send_emails.py...")
    result = subprocess.run(
        [sys.executable, "send_emails.py"],
        capture_output=False,
    )
    if result.returncode != 0:
        log.error("send_emails.py exited with errors.")


def main():
    if "--now" in sys.argv:
        run_send()
        return

    log.info(f"Scheduler started. Will send daily at {config.SEND_HOUR_START}:00.")
    last_run_date = None

    while True:
        now = datetime.now()
        today = now.date()

        if (
            now.hour == config.SEND_HOUR_START
            and last_run_date != today
        ):
            run_send()
            last_run_date = today

        time.sleep(60)  # Check every minute


if __name__ == "__main__":
    main()
