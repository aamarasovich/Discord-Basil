import discord
from discord.ext import commands
import asyncio
import re # For parsing time string
from datetime import timedelta

# Helper function to parse time strings like "10m", "1h", "2d5h10m"
def parse_time(time_str: str) -> int:
    """Parses a time string and returns the total seconds."""
    regex = re.compile(r'((?P<days>\d+)d)?((?P<hours>\d+)h)?((?P<minutes>\d+)m)?((?P<seconds>\d+)s)?')
    parts = regex.match(time_str)
    if not parts:
        return 0
    parts = parts.groupdict()
    time_params = {}
    for name, param in parts.items():
        if param:
            time_params[name] = int(param)
    delta = timedelta(**time_params)
    return int(delta.total_seconds())

class ReminderCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='remindme', help='Sets a reminder. Usage: !remindme <time> <message> (e.g., !remindme 1h30m Check the oven)')
    async def remindme(self, ctx: commands.Context, time_str: str, *, reminder_message: str):
        """Sets a reminder for the user."""

        seconds = parse_time(time_str)

        if seconds <= 0:
            await ctx.send("Invalid time format. Please use d, h, m, s (e.g., '1d', '2h30m', '10m', '5s').")
            return

        # Optional: Add a reasonable maximum time limit
        max_seconds = 60 * 60 * 24 * 30 # e.g., 30 days
        if seconds > max_seconds:
             await ctx.send(f"Sorry, the maximum reminder time is 30 days.")
             return

        requester = ctx.author
        channel = ctx.channel

        # Confirm reminder set
        await ctx.send(f"Okay {requester.mention}, I will remind you about '{reminder_message}' in {time_str}.")

        # Wait for the specified duration
        await asyncio.sleep(seconds)

        # Send the reminder
        try:
            # Try sending in the original channel, mentioning the user
            await channel.send(f"{requester.mention}, here is your reminder: {reminder_message}")
        except discord.Forbidden:
            # If sending in channel fails (e.g., permissions lost), try DM
            try:
                 await requester.send(f"Hi {requester.mention}, here is your reminder from the '{ctx.guild.name}' server: {reminder_message}")
            except discord.Forbidden:
                 # If DM also fails, can't do much else
                 print(f"Could not send reminder to {requester.name} (ID: {requester.id})")
        except discord.HTTPException as e:
             print(f"Failed to send reminder due to HTTPException: {e}")


# The setup function that discord.py runs to load the cog
async def setup(bot):
    await bot.add_cog(ReminderCog(bot))