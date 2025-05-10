from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime

def get_google_services():
    creds = Credentials.from_authorized_user_file('token.json', ['https://www.googleapis.com/auth/calendar.readonly', 'https://www.googleapis.com/auth/tasks.readonly'])
    calendar_service = build('calendar', 'v3', credentials=creds)
    tasks_service = build('tasks', 'v1', credentials=creds)
    return calendar_service, tasks_service

def get_today_events(service):
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    end_of_day = (datetime.datetime.utcnow().replace(hour=23, minute=59, second=59)).isoformat() + 'Z'

    events_result = service.events().list(
        calendarId='primary', timeMin=now, timeMax=end_of_day,
        singleEvents=True, orderBy='startTime'
    ).execute()
    return events_result.get('items', [])

def get_today_tasks(service):
    tasklists = service.tasklists().list().execute()
    tasks_today = []
    for tasklist in tasklists.get('items', []):
        tasks = service.tasks().list(tasklist=tasklist['id']).execute()
        for task in tasks.get('items', []):
            due = task.get('due')
            if due and datetime.datetime.fromisoformat(due[:-1]).date() == datetime.datetime.utcnow().date():
                tasks_today.append(task)
    return tasks_today
