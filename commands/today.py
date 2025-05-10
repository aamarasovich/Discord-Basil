import discord
from discord.ext import commands
from google_services import get_google_services, get_today_events, get_today_tasks

class Today(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="today")
    async def today(self, ctx):
        """
        Retrieves and displays today's Google Calendar events and Google Tasks.
        """
        try:
            # Initialize Google services
            calendar_service, tasks_service = get_google_services()  # Removed 'await'

            # Fetch today's events and tasks
            events = get_today_events(calendar_service)  # Removed 'await'
            tasks = get_today_tasks(tasks_service)  # Removed 'await'

            # Format the response
            response = "**📅 Today's Events:**\n"
            if events:
                for event in events:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    response += f"- {event['summary']} at {start}\n"
            else:
                response += "No events today.\n"

            response += "\n**📝 Today's Tasks:**\n"
            if tasks:
                for task in tasks:
                    response += f"- {task['title']}\n"
            else:
                response += "No tasks due today."

            # Send the response
            await ctx.send(response)

        except Exception as e:
            # Handle errors gracefully
            await ctx.send("An error occurred while retrieving today's events and tasks.")
            print(f"Error in 'today' command: {e}")

# Setup function to add the Cog
async def setup(bot):
    await bot.add_cog(Today(bot))
