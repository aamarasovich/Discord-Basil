import discord
from discord.ext import commands
from google_services import get_google_services, get_today_events, get_today_tasks, list_calendars, list_task_lists, load_user_credentials
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
                
        except Exception as e:
            await ctx.send("An error occurred while retrieving today's events and tasks.")
            logger.error(f"Error in 'today' command: {e}")

# Setup function to add the Cog
async def setup(bot):
    await bot.add_cog(Today(bot))
