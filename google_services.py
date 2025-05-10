import os
import json
import logging
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from datetime import datetime, timezone
import pytz  # Import pytz for timezone handling
from discord.ext import commands

# Set up logging
logger = logging.getLogger("google_services")
logging.basicConfig(level=logging.INFO)

def get_google_services():
    """
    Initializes Google Calendar and Tasks services using credentials from the environment.
    """
    try:
        # Load credentials from the environment variable
        credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
        if not credentials_json:
            raise ValueError("GOOGLE_CREDENTIALS_JSON environment variable is not set.")

        # Parse the JSON string into a dictionary
        credentials_dict = json.loads(credentials_json)

        # Create credentials object
        credentials = Credentials.from_service_account_info(credentials_dict)

        # Initialize Google Calendar and Tasks services with cache_discovery=False
        calendar_service = build("calendar", "v3", credentials=credentials, cache_discovery=False)
        tasks_service = build("tasks", "v1", credentials=credentials, cache_discovery=False)

        return calendar_service, tasks_service
    except Exception as e:
        logger.error(f"Error initializing Google services: {e}")
        raise

def get_today_events(service):
    """
    Fetches today's events from Google Calendar in the local timezone.
    """
    try:
        # Define the local timezone (e.g., Eastern Time)
        eastern = pytz.timezone('America/New_York')

        # Get the start and end of the day in the local timezone
        now = datetime.now(eastern)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Log the time range for debugging
        logger.info(f"Fetching events from {start_of_day} to {end_of_day} in Eastern Time")

        # Query Google Calendar API
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_of_day.isoformat(),
            timeMax=end_of_day.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        return events_result.get('items', [])
    except Exception as e:
        logger.error(f"Error fetching today's events: {e}")
        return []

def get_today_tasks(service):
    """
    Fetches today's tasks from Google Tasks in the local timezone.
    """
    try:
        # Define the local timezone (e.g., Eastern Time)
        eastern = pytz.timezone('America/New_York')

        # Get today's date in the local timezone
        today = datetime.now(eastern).date()
        logger.info(f"Fetching tasks for {today} in Eastern Time")

        # Query Google Tasks API
        tasklists = service.tasklists().list().execute()
        tasks_today = []
        for tasklist in tasklists.get('items', []):
            tasks = service.tasks().list(tasklist=tasklist['id']).execute()
            for task in tasks.get('items', []):
                due = task.get('due')
                if due:
                    # Convert the due date to the local timezone
                    due_date = datetime.fromisoformat(due[:-1]).astimezone(eastern).date()
                    if due_date == today:
                        tasks_today.append(task)
        return tasks_today
    except Exception as e:
        logger.error(f"Error fetching today's tasks: {e}")
        return []

def list_calendars(service):
    """
    Lists all calendars accessible by the authenticated account.
    """
    try:
        calendars = service.calendarList().list().execute()
        for calendar in calendars.get('items', []):
            logger.info(f"Calendar: {calendar['summary']} (ID: {calendar['id']})")
    except Exception as e:
        logger.error(f"Error listing calendars: {e}")

class Today(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="today")
    async def today(self, ctx):
        try:
            # Debug: Check if GOOGLE_CREDENTIALS_JSON is accessible
            if not os.getenv("GOOGLE_CREDENTIALS_JSON"):
                await ctx.send("GOOGLE_CREDENTIALS_JSON is not set in the environment.")
                return

            # Initialize Google services
            calendar_service, tasks_service = get_google_services()

            # Fetch today's events and tasks
            events = get_today_events(calendar_service)
            tasks = get_today_tasks(tasks_service)

            # Format and send the response
            response = "**📅 Today's Events:**\n"
            response += "No events today.\n" if not events else "\n".join(
                f"- {event['summary']} at {event['start'].get('dateTime', event['start'].get('date'))}" for event in events
            )
            response += "\n\n**📝 Today's Tasks:**\n"
            response += "No tasks due today." if not tasks else "\n".join(f"- {task['title']}" for task in tasks)

            await ctx.send(response)
        except Exception as e:
            await ctx.send("An error occurred while retrieving today's events and tasks.")
            logger.error(f"Error in 'today' command: {e}")
