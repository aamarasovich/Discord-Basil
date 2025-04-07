import os
import json
import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from dateutil import parser  # Make sure 'python-dateutil' is in your requirements.txt
import pytz

def get_upcoming_events():
    # 🌐 Load service account credentials from Railway environment variable
    json_str = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if not json_str:
        return "No credentials found 😢"

    creds_dict = json.loads(json_str)
    creds = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=['https://www.googleapis.com/auth/calendar.readonly']
    )

    # 🧭 Set timezone to America/New_York
    local_tz = pytz.timezone("America/New_York")
    now = datetime.datetime.now(local_tz)
    print(f"📅 Basil thinks it’s currently: {now.isoformat()}")
    end = now + datetime.timedelta(days=2)
    now_iso = now.isoformat()
    end_iso = end.isoformat()

    # 🗓️ Connect to Google Calendar
    service = build('calendar', 'v3', credentials=creds)

    events_result = service.events().list(
        calendarId='primary',
        timeMin=now_iso,
        timeMax=end_iso,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])

    # 📋 Debug output
    print(f"✅ Basil sees {len(events)} events coming up:")
    for e in events:
        start_info = e.get('start', {})
        start = start_info.get('dateTime') or start_info.get('date') or "No start time"
        summary = e.get('summary', 'No title')
        print(f"• {start} — {summary}")

    if not events:
        return "You have no events today or tomorrow ✨"

    # 🎯 Filter events into today and tomorrow
    output = {"today": [], "tomorrow": []}
    for event in events:
        start_str = event.get('start', {}).get('dateTime') or event.get('start', {}).get('date')
        try:
            start = parser.parse(start_str).astimezone(local_tz)
        except Exception as e:
            print(f"⚠️ Could not parse date for event: {event.get('summary', 'No title')} — {e}")
            continue

        summary = event.get('summary', 'No title')
        if start.date() == now.date():
            output["today"].append((start, summary))
        elif start.date() == (now + datetime.timedelta(days=1)).date():
            output["tomorrow"].append((start, summary))

    # ✨ Format event list output
    def format_event_list(label, event_list):
        if not event_list:
            return ""
        lines = [f"**{label.capitalize()}:**"]
        for start, summary in event_list:
            if start.time() != datetime.time(0, 0):
                time_str = start.strftime("%-I:%M %p").lstrip("0")
                lines.append(f"• {summary} at {time_str}")
            else:
                lines.append(f"• {summary}")
        return "\n".join(lines)

    today_text = format_event_list("today", output["today"])
    tomorrow_text = format_event_list("tomorrow", output["tomorrow"])

    return "\n\n".join(filter(None, [today_text, tomorrow_text]))
