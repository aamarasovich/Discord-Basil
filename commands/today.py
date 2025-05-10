import discord
from discord.ext import commands
from google_services import get_google_services, get_today_events, get_today_tasks, list_calendars, list_task_lists
import os
import logging

logger = logging.getLogger(__name__)

class Today(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="today")
    async def today(self, ctx):
        """
        Retrieves and displays today's Google Calendar events and Google Tasks.
        """
        try:
            # Debug: Check if GOOGLE_CREDENTIALS_JSON is accessible
            if not os.getenv("GOOGLE_CREDENTIALS_JSON"):
                await ctx.send("GOOGLE_CREDENTIALS_JSON is not set in the environment.")
                return

            # Initialize Google services
            calendar_service, tasks_service = get_google_services()

            # Debug: List all available calendars
            list_calendars(calendar_service)
            await ctx.send("Check the logs for available calendars.")

            # Debug: List all available task lists
            list_task_lists(tasks_service)
            await ctx.send("Check the logs for available task lists.")

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

# Setup function to add the Cog
async def setup(bot):
    await bot.add_cog(Today(bot))
