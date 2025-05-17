import os
import json
import logging
from google.oauth2.service_account import Credentials
from google.oauth2.credentials import Credentials as UserCredentials
from googleapiclient.discovery import build
from datetime import datetime, timezone
import pytz  # Import pytz for timezone handling
from discord.ext import commands
import pickle
import os.path

# Set up logging
logger = logging.getLogger("google_services")
logging.basicConfig(level=logging.INFO)

# Directory to store user credentials
CREDENTIALS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'user_credentials')
os.makedirs(CREDENTIALS_DIR, exist_ok=True)

def get_user_credentials_path(user_id):
    """Get the path to a user's credentials file"""
    return os.path.join(CREDENTIALS_DIR, f'user_{user_id}.pickle')

def save_user_credentials(user_id, credentials):
    """Save OAuth credentials for a user"""
    try:
        credentials_path = get_user_credentials_path(user_id)
        with open(credentials_path, 'wb') as token:
            pickle.dump(credentials, token)
        logger.info(f"Saved credentials for user {user_id}")
        return True
    except Exception as e:
        logger.error(f"Error saving user credentials: {e}")
        return False

def load_user_credentials(user_id):
    """Load OAuth credentials for a user if they exist"""
    credentials_path = get_user_credentials_path(user_id)
    if os.path.exists(credentials_path):
        with open(credentials_path, 'rb') as token:
            credentials = pickle.load(token)
        return credentials
    return None

def get_google_services(user_id=None):
    """
<<<<<<< HEAD
    Initializes Google Calendar and Tasks services using credentials from environment variable.
=======
    Initializes Google Calendar and Tasks services.
    If user_id is provided, tries to use their OAuth credentials.
    Otherwise falls back to service account credentials from environment.
>>>>>>> e3673f0b67278ad62040dc153705673fbe6886c8
    """
    try:
        # If user_id is provided, try to load their credentials
        if user_id:
            credentials = load_user_credentials(user_id)
            if credentials:
                logger.info(f"Using OAuth credentials for user {user_id}")
                calendar_service = build("calendar", "v3", credentials=credentials, cache_discovery=False)
                tasks_service = build("tasks", "v1", credentials=credentials, cache_discovery=False)
                
                # Test connection
                calendar_service.calendarList().list(maxResults=1).execute()
                logger.info("Successfully connected to Google Calendar API with user credentials")
                return calendar_service, tasks_service
            else:
                logger.info(f"No saved credentials found for user {user_id}")
                # If we're explicitly looking for user credentials but didn't find any,
                # raise an error rather than falling back to service account
                raise ValueError("User has not connected their Google account yet")
        
        # Only use service account if not looking for user-specific credentials
        logger.info("Using service account credentials")
        
        # Load credentials from the environment variable
        credentials_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
        if not credentials_json:
            raise ValueError("GOOGLE_CREDENTIALS_JSON environment variable is not set.")

        # Parse the JSON string into a dictionary
        credentials_dict = json.loads(credentials_json)
        
        # Check credential type
        if 'type' in credentials_dict and credentials_dict['type'] == 'service_account':
            # Validate required fields for service account
            required_fields = ['client_email', 'private_key', 'token_uri']
            missing_fields = [field for field in required_fields if field not in credentials_dict]
            
            if missing_fields:
                missing_fields_str = ', '.join(missing_fields)
                raise ValueError(f"Service account credentials missing required fields: {missing_fields_str}")
            
            # Create service account credentials
            logger.info("Using service account for authentication")
            credentials = Credentials.from_service_account_info(credentials_dict)
            
            # Initialize Google Calendar and Tasks services with cache_discovery=False
            calendar_service = build("calendar", "v3", credentials=credentials, cache_discovery=False)
            tasks_service = build("tasks", "v1", credentials=credentials, cache_discovery=False)

<<<<<<< HEAD
        # Create credentials object with necessary scopes
        credentials = Credentials.from_service_account_info(
            credentials_dict,
            scopes=['https://www.googleapis.com/auth/calendar.readonly',
                   'https://www.googleapis.com/auth/tasks.readonly']
        )

        # Initialize services
        calendar_service = build("calendar", "v3", credentials=credentials, cache_discovery=False)
        tasks_service = build("tasks", "v1", credentials=credentials, cache_discovery=False)

        return calendar_service, tasks_service
=======
            # Test the connection by making a simple API call
            calendar_service.calendarList().list(maxResults=1).execute()
            logger.info("Successfully connected to Google Calendar API with service account")
            
            return calendar_service, tasks_service
        else:
            # We have OAuth client credentials, not service account credentials
            raise ValueError("OAuth client credentials detected instead of service account credentials.")
    except ValueError as ve:
        logger.error(f"Credentials error: {ve}")
        raise
>>>>>>> e3673f0b67278ad62040dc153705673fbe6886c8
    except Exception as e:
        logger.error(f"Error initializing Google services: {e}")
        raise

def get_today_events(service):
    """
    Fetches today's events from all accessible Google Calendars in the local timezone.
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
        
        # Get all available calendars
        logger.info("Fetching events from all available calendars")
        all_events = []
        calendars = service.calendarList().list().execute()
        calendar_count = len(calendars.get('items', []))
        logger.info(f"Found {calendar_count} calendars to check")
        
        # Process each calendar with rate limiting
        for i, calendar in enumerate(calendars.get('items', [])):
            calendar_id = calendar.get('id')
            calendar_name = calendar.get('summary', 'Unnamed')
            
            # Log which calendar we're checking
            logger.info(f"Checking calendar {i+1}/{calendar_count}: {calendar_name} (ID: {calendar_id})")
            
            try:
                # Rate limiting - sleep for a short time between requests
                # More time between requests as we process more calendars
                if i > 0:
                    import time
                    time.sleep(0.2)  # 200ms delay between calendar queries
                
                # Query this calendar
                events_result = service.events().list(
                    calendarId=calendar_id,
                    timeMin=start_of_day.isoformat(),
                    timeMax=end_of_day.isoformat(),
                    singleEvents=True,
                    orderBy='startTime'
                ).execute()
                
                calendar_events = events_result.get('items', [])
                
                # Add calendar name to each event for reference
                for event in calendar_events:
                    event['calendarName'] = calendar_name
                
                # Add events from this calendar to our combined list
                all_events.extend(calendar_events)
                logger.info(f"Found {len(calendar_events)} events in calendar '{calendar_name}'")
                
            except Exception as e:
                logger.error(f"Error fetching events from calendar '{calendar_name}': {e}")
                # Continue to next calendar even if this one fails
                continue
        
        # Sort all events by start time
        all_events.sort(key=lambda x: x['start'].get('dateTime', x['start'].get('date', '')) if x.get('start') else '')
        
        logger.info(f"Total events found across all calendars: {len(all_events)}")
        return all_events
        
    except Exception as e:
        logger.error(f"Error fetching today's events: {e}")
        return []

def get_today_tasks(service):
    """
    Fetches today's tasks from all Google Task lists in the local timezone.
    """
    try:
        # Define the local timezone (e.g., Eastern Time)
        eastern = pytz.timezone('America/New_York')

        # Get today's date in the local timezone
        today = datetime.now(eastern).date()
        logger.info(f"Fetching tasks for {today} in Eastern Time")

        # Query Google Tasks API for all task lists
        logger.info("Fetching tasks from all available task lists")
        tasklists = service.tasklists().list().execute()
        all_tasks_today = []
        tasklist_count = len(tasklists.get('items', []))
        logger.info(f"Found {tasklist_count} task lists to check")
        
        # Process each task list with rate limiting
        for i, tasklist in enumerate(tasklists.get('items', [])):
            tasklist_id = tasklist.get('id')
            tasklist_title = tasklist.get('title', 'Unnamed')
            
            # Log which task list we're checking
            logger.info(f"Checking task list {i+1}/{tasklist_count}: {tasklist_title} (ID: {tasklist_id})")
            
            try:
                # Rate limiting - sleep for a short time between requests
                if i > 0:
                    import time
                    time.sleep(0.2)  # 200ms delay between task list queries
                
                # Query this task list
                tasks = service.tasks().list(tasklist=tasklist_id).execute()
                
                # Find tasks due today
                tasks_found = 0
                for task in tasks.get('items', []):
                    due = task.get('due')
                    if due:
                        # Convert the due date to the local timezone
                        due_date = datetime.fromisoformat(due[:-1]).astimezone(eastern).date()
                        if due_date == today:
                            # Add task list name for reference
                            task['taskListName'] = tasklist_title
                            all_tasks_today.append(task)
                            tasks_found += 1
                
                logger.info(f"Found {tasks_found} tasks due today in task list '{tasklist_title}'")
                
            except Exception as e:
                logger.error(f"Error fetching tasks from task list '{tasklist_title}': {e}")
                # Continue to next task list even if this one fails
                continue
        
        logger.info(f"Total tasks found due today across all task lists: {len(all_tasks_today)}")
        return all_tasks_today
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

def list_task_lists(service):
    """
    Lists all task lists accessible by the authenticated account.
    """
    try:
        tasklists = service.tasklists().list().execute()
        for tasklist in tasklists.get('items', []):
            logger.info(f"Task List: {tasklist['title']} (ID: {tasklist['id']})")
    except Exception as e:
        logger.error(f"Error listing task lists: {e}")

class Today(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="today")
    async def today(self, ctx):
        try:
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
