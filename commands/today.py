import discord
from discord.ext import commands
<<<<<<< HEAD
from google_services import get_google_services, get_today_events, get_today_tasks
=======
from google_services import get_google_services, get_today_events, get_today_tasks, list_calendars, list_task_lists, load_user_credentials
import os
>>>>>>> e3673f0b67278ad62040dc153705673fbe6886c8
import logging
from datetime import datetime
import pytz

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
<<<<<<< HEAD
            # Send loading message
            loading_msg = await ctx.send("📅 Fetching your schedule...")

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

=======
            # Get the user's Discord ID
            user_id = str(ctx.author.id)
            
            # First, try to use the user's OAuth credentials
            try:
                # Initialize Google services with user's credentials
                calendar_service, tasks_service = get_google_services(user_id)
                
                # Fetch today's events and tasks
                events = get_today_events(calendar_service)
                tasks = get_today_tasks(tasks_service)
                
                # Debug: List all available calendars and task lists
                list_calendars(calendar_service)
                await ctx.send("Check the logs for available calendars.")
                list_task_lists(tasks_service)
                await ctx.send("Check the logs for available task lists.")
                
                # Format and send the response
                response = "**📅 Today's Events:**\n"
                response += "No events today.\n" if not events else "\n".join(
                    f"- {event['summary']} at {event['start'].get('dateTime', event['start'].get('date'))}" for event in events
                )
                response += "\n\n**📝 Today's Tasks:**\n"
                response += "No tasks due today." if not tasks else "\n".join(f"- {task['title']}" for task in tasks)
                
                await ctx.send(response)
                
            except Exception as e:
                logger.error(f"Error using user credentials: {e}")
                
                # If no valid user credentials or other error, prompt them to connect
                base_url = os.getenv("BASE_URL", "http://localhost:8000")
                auth_url = f"{base_url}/authorize?user_id={user_id}"
                
                embed = discord.Embed(
                    title="Google Calendar Not Connected",
                    description="You need to connect your Google account to use this command.",
                    color=discord.Color.blue()
                )
                embed.add_field(
                    name="Connect Your Account", 
                    value=f"Use the `!connect_google` command to connect your Google Calendar and Tasks."
                )
                embed.set_footer(text="Your data will only be accessible to you.")
                
                await ctx.send(embed=embed)
                
>>>>>>> e3673f0b67278ad62040dc153705673fbe6886c8
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
