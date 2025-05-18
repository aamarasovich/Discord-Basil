import discord
from discord.ext import commands
from google_services import get_google_services, get_today_events, get_today_tasks
import logging
import pytz
from datetime import datetime

logger = logging.getLogger(__name__)

class Today(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def format_time(self, time_str):
        """Helper to format time strings"""
        try:
            if 'T' in time_str:  # DateTime format
                dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
                return dt.astimezone(pytz.timezone('America/New_York')).strftime("%I:%M %p")
            return "All day"  # Date only format
        except:
            return "Time unknown"

    @commands.command(name="today")
    async def today(self, ctx):
        """Retrieves and displays today's Google Calendar events and Google Tasks."""
        try:
            # Send loading message
            loading_msg = await ctx.send("📅 Fetching your schedule...")

            try:
                # Initialize Google services
                calendar_service, tasks_service = get_google_services()
                
                # Fetch data
                events = get_today_events(calendar_service)
                tasks = get_today_tasks(tasks_service)

                # Format events
                response = "**📅 Today's Schedule:**\n\n"
                if events:
                    for event in events:
                        start_time = self.format_time(event['start'].get('dateTime', event['start'].get('date')))
                        response += f"⏰ `{start_time}` - {event['summary']}\n"
                else:
                    response += "No events scheduled today\n"

                # Format tasks
                response += "\n**📝 Today's Tasks:**\n"
                if tasks:
                    for task in tasks:
                        status = "✅" if task.get('completed') else "⬜"
                        response += f"{status} {task['title']}\n"
                else:
                    response += "No tasks due today"

                # Edit the loading message with the results
                await loading_msg.edit(content=response)
                
            except Exception as e:
                # If there's an error with Google services, show a generic error message
                error_msg = "⚠️ Error retrieving your schedule. Please try again later."
                logger.error(f"Error in 'today' command: {str(e)}")
                await loading_msg.edit(content=error_msg)

        except Exception as e:
            error_msg = "⚠️ Error retrieving your schedule. Please try again later."
            logger.error(f"Error in 'today' command: {str(e)}")
            if 'loading_msg' in locals():
                await loading_msg.edit(content=error_msg)
            else:
                await ctx.send(error_msg)

# Setup function to add the Cog
async def setup(bot):
    await bot.add_cog(Today(bot))
