# calendar_utils.py (or top of your main bot file)
import os
import json
from google.oauth2 import service_account

def get_upcoming_events():
    creds = None

    json_str = os.getenv("GOOGLE_CREDENTIALS_JSON")
    if not json_str:
        return "No credentials found 😢"

    creds_dict = json.loads(json_str)
    creds = service_account.Credentials.from_service_account_info(
        creds_dict,
        scopes=['https://www.googleapis.com/auth/calendar.readonly']
    )

    service = build('calendar', 'v3', credentials=creds)

    # Everything else (fetching + formatting) stays the same

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

print(f"✅ Basil sees {len(events)} events coming up:")
for e in events:
    start = e['start'].get('dateTime', e['start'].get('date'))
    print(f"• {start} — {e.get('summary')}")

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
