from datetime import datetime, time, timedelta
import subprocess
import sys

import NotificationEmail
import applicationStartupMail
import utility
import os
import datetime as datetime
from datetime import datetime as datetimenow, timedelta
import imaplib
import email
import time
from email.utils import parsedate_to_datetime
from datetime import datetime
import re
from gettext import find
from zoneinfo import ZoneInfo  # ✅ Requires Python 3.9+

import OHLCdata

import OHLCdata
import applicationStartupMail
import findStockLiveOnly
import logging

required_packages = {
    'requests': 'requests',
    'bs4': 'beautifulsoup4',
    'progressbar': 'progressbar2',
    'lxml': 'lxml',
    'time': 'time',
    'datetime': 'datetime',
    'sys': 'sys',
    'NotificationEmail': 'NotificationEmail',
    'os': 'os'
}



# Step 1: Get today's date string (e.g., 2025-06-16)
today_str = datetimenow.now().strftime("%Y-%m-%d")

# Step 2: Create the log filename
log_filename = f"console_log_{today_str}.txt"

# Step 3: Ensure the directory exists (optional)
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, log_filename)


# Create and configure logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path, mode='a'),  # 'a' ensures appending if file exists
        logging.StreamHandler(sys.stdout)
    ]
)

def install_package(pip_name):
    subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])

for module, pip_name in required_packages.items():
    try:
        __import__(module)
    except ImportError:
        print(f"{module} not found. Installing {pip_name}...")
        install_package(pip_name)

# Email account credentials
EMAIL = 'shahuk23@gmail.com'
PASSWORD = 'sppb msat ckqt tife'  # Use an app password if using Gmail with 2FA
IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993
LABEL = 'chartink'  # 👈 your Gmail label name (case-sensitive)
testOffTime = True
isEmailRequired = True
isMarketCloseCheckRequired = True
isDevOrProdEnvironment = 'DEV'
maintain_unique_stocks = []
maintain_unique_stocksList_for_email = []

def fetch_recent_labeled_emails(window_minutes=2):
    print("🔁 Checking for Email Alerts...")

    mail = imaplib.IMAP4_SSL("imap.gmail.com")
    mail.login(EMAIL, PASSWORD)

    status, _ = mail.select(f'"{LABEL}"')
    if status != "OK":
        print(f"❌ Failed to open label '{LABEL}'")
        return

    # Search for emails with specific subject
    status, data = mail.search(None, '(SUBJECT "[Scan alert \\"<<<VCP>>>\\"]")')
    if not data or not data[0]:
        print("📭 No matching emails found in label.")
        return

    email_ids = data[0].split()
    now_ist = datetime.now(ZoneInfo("Asia/Kolkata"))

    recent_found = False

    for eid in reversed(email_ids):  # Loop from latest to oldest
        res, msg_data = mail.fetch(eid, '(RFC822)')
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        # Convert email date to IST
        email_date_header = msg['Date']
        parsed_date = parsedate_to_datetime(email_date_header)
        ist_time = parsed_date.astimezone(ZoneInfo("Asia/Kolkata"))
        diff = (now_ist - ist_time).total_seconds() / 60  # in minutes

        if diff > window_minutes:
            break  # Stop checking older emails

        recent_found = True
        print(f"📩 New Email at {ist_time.strftime('%Y-%m-%d %I:%M %p')} IST")

        # Extract plain text body
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/plain':
                    body = part.get_payload(decode=True).decode(errors='ignore')
                    break
        else:
            body = msg.get_payload(decode=True).decode(errors='ignore')

        # Extract stock info
        lines = body.splitlines()
        capture = False
        for line in lines:
            if isinstance(line, bytes):
                line = line.decode('utf-8', errors='ignore')  # Decode bytes to str

            line = line.strip()
            if not line:
                continue
            if "filtered through scan" in line.lower():
                capture = True
                continue
            if capture:
                if line.startswith("View all") or line.startswith("©"):
                    break
                stock_info = f"{line} (Email time: {ist_time.strftime('%Y-%m-%d %I:%M %p')})"
                print("🔍 Found:", stock_info)

                # Extract and fetch OHLC
                stock_name, date, time = extract_stock_name_and_time(stock_info)

                stockData = OHLCdata.fetch_ohlc_close_by_email_time(stock_name, date, time)
                findStockLiveOnly.process_buy_signals_from_email_scrap(stockData)

    if not recent_found:
        print("⚠️ No recent emails in the last", window_minutes, "minutes.")

    print("🔚 Loging out")
    mail.logout()
def extract_stock_name_and_time(entry):
    """
    Extract stock name and email time from a string like:
    'NH (Email time: 2025-08-01 09:16 AM)'

    Returns:
        tuple: (stock_name: str, email_time: datetime)
    """
    match = re.match(r"(\w+)\s+\(Email time:\s+([\d\-]+\s+[\d:]+\s+[APM]+)\)", entry)
    if match:
        stock_name = match.group(1)
        email_time_str = match.group(2)
        email_datetime = datetime.strptime(email_time_str, "%Y-%m-%d %I:%M %p")

        email_date = email_datetime.date()    # Extract date
        email_time = email_datetime.time()    # Extract time
        print(f"⏳ Waiting 5 Minutes to close candle...")
       # time.sleep(300)
        return stock_name, email_date, email_time
    else:
        raise ValueError("Invalid format")


def checkMarketOffTime():
    utc_now = datetimenow.utcnow()
    ist_now = utc_now + timedelta(hours=5, minutes=30)

    # Check if time is 3:30 PM or later
    if ist_now.hour > 15 or (ist_now.hour == 15 and ist_now.minute >= 30):
        logging.info(f"Time is 3:30 PM IST or later. Quitting application.")
        print("Time is 3:30 PM IST or later. Quitting application.")
        if maintain_unique_stocks:
            NotificationEmail.sendEmailAtEOD(maintain_unique_stocks)

        quit()  # or use sys.exit() for clarity


if __name__ == "__main__":
    if isDevOrProdEnvironment == 'PROD':
        applicationStartupMail.sendEmailOnStart()

        logging.info(f"********* Welcome to SK Trading App *********")
        logging.info(f"********* prop. Shahu Kshirsagar *********\n")
        print("********* Welcome to SK Trading App *********")
        print("********* prop. Shahu Kshirsagar *********\n")
        maintain_unique_stocks = utility.load_stocks_from_csv()
    while True:
        if(isMarketCloseCheckRequired):
            if isDevOrProdEnvironment == 'PROD':
                checkMarketOffTime()

        fetch_recent_labeled_emails(window_minutes=1500)
        time.sleep(60)
