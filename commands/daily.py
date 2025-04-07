import os
import json
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dateutil import parser  # make sure this is in requirements.txt
import pytz

def get_upcoming_events():
    json_str = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if not json_str:
        return "No credentials found 😢"

    creds_dict = json.loads(json_str)
    creds = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=['https://www.googleapis.com/auth/calendar.readonly']
    )

    # ✨ connect to Google Calendar uwu
    service = build('calendar', 'v3', credentials=creds)

    # 🧠 figure out what time Basil thinks it is
    local_tz = pytz.timezone("America/New_York")
    now = datetime.datetime.now(local_tz)
    print(f"📅 Basil thinks it's currently: {now.isoformat()}")
    end = now + datetime.timedelta(days=2)
    now_iso = now.isoformat()
    end_iso = end.isoformat()

    # 🕵️‍♀️ let's see ALL calendars we can read
    calendars = service.calendarList().list().execute()
    for cal in calendars.get('items', []):
        print(f"📆 Found calendar: {cal['summary']} (ID: {cal['id']})")

    # ⛔ STOP HERE after pushing — check Railway logs before continuing
    return "Logged available calendars! Check Railway logs and tell ChatGPT which one is yours ✨"
