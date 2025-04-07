import os
import json
import datetime
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dateutil import parser
import pytz

def get_upcoming_events():
    # 🔐 Load credentials from Railway environment variable
    json_str = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if not json_str:
        return "No credentials found 😢"

    creds_dict = json.loads(json_str)
    creds = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=['https://www.googleapis.com/auth/calendar.readonly']
    )

    # 📆 Connect to the Calendar API
    service = build('calendar', 'v3', credentials=creds)

    # ⏰ Use America/New_York time zone so Basil thinks like you do
    local_tz = pytz.timezone("America/New_York")
    now = datetime.datetime.now(local_tz)
    print(f"📅 Basil thinks it’s currently: {now.isoformat()}")

    # 🕵️‍♀️ Check which calendars we have access to
    calendars = service.calendarList().list().execute()
    for cal in calendars.get('items', []):
        logging.info(f"📆 Found calendar: {cal['summary']} (ID: {cal['id']})")
    # ⛔ Don’t continue yet — let’s review in the logs first
    return "Logged available calendars! Check Railway logs and tell ChatGPT which one is yours ✨"
