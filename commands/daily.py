# calendar_utils.py (or top of your main bot file)

import datetime
import os.path
import pickle

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from dateutil import parser  # you'll need to add `python-dateutil` to requirements.txt

SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def get_upcoming_events():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            'client_secret_*.json', SCOPES
        )
        creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    now = datetime.datetime.now(datetime.timezone.utc)
    end = now + datetime.timedelta(days=2)
    now_iso = now.isoformat()
    end_iso = end.isoformat()

    events_result = service.events().list(
        calendarId='primary',
        timeMin=now_iso,
        timeMax=end_iso,
        singleEvents=True,
        orderBy='startTime'
    ).execute()

    events = events_result.get('items', [])

    if not events:
        return "You have no events today or tomorrow ✨"

    output = {"today": [], "tomorrow": []}

    for event in events:
        start_str = event['start'].get('dateTime', event['start'].get('date'))
        start = parser.parse(start_str)
        summary = event.get('summary', 'No title')

        if start.date() == now.date():
            output["today"].append((start, summary))
        elif start.date() == (now + datetime.timedelta(days=1)).date():
            output["tomorrow"].append((start, summary))

    def format_event_list(label, event_list):
        if not event_list:
            return ""
        lines = [f"**{label.capitalize()}:**"]
        for start, summary in event_list:
            time_str = start.strftime("%-I:%M %p") if start.time() != datetime.time(0, 0) else ""
            lines.append(f"• {summary} at {time_str}".strip())
        return "\n".join(lines)

    today_text = format_event_list("today", output["today"])
    tomorrow_text = format_event_list("tomorrow", output["tomorrow"])

    return "\n\n".join(filter(None, [today_text, tomorrow_text]))
