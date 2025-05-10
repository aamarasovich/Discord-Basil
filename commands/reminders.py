import re
from datetime import datetime, timedelta
import discord
from discord.ext import commands

class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="remindme")
    async def remindme(self, ctx, *, time_input: str):
        """
        Sets a reminder for the user. Accepts both time increments (e.g., '1h30m')
        and specific date/time formats (e.g., '2025-05-10 14:30').
        """
        try:
            # Check if input is a specific date/time
            try:
                reminder_time = datetime.strptime(time_input, "%Y-%m-%d %H:%M")
                now = datetime.now()
                if reminder_time <= now:
                    await ctx.send("The specified time is in the past. Please provide a future time.")
                    return
                delay = (reminder_time - now).total_seconds()
            except ValueError:
                # If not a date/time, parse as time increment
                time_pattern = re.compile(r'((?P<hours>\d+)h)?((?P<minutes>\d+)m)?')
                match = time_pattern.fullmatch(time_input)
                if not match:
                    await ctx.send("Invalid time format. Use '1h30m' for increments or 'YYYY-MM-DD HH:MM' for specific times.")
                    return

                time_data = match.groupdict()
                hours = int(time_data['hours']) if time_data['hours'] else 0
                minutes = int(time_data['minutes']) if time_data['minutes'] else 0
                delay = timedelta(hours=hours, minutes=minutes).total_seconds()

            if delay <= 0:
                await ctx.send("The specified time is invalid. Please provide a future time.")
                return

            # Schedule the reminder
            await ctx.send(f"Reminder set! I'll remind you in {time_input}.")
            await discord.utils.sleep_until(datetime.now() + timedelta(seconds=delay))
            await ctx.author.send(f"⏰ Reminder: {time_input}")

        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

async def setup(bot):
    await bot.add_cog(Reminders(bot))