import re
from datetime import datetime, timedelta
import discord
from discord.ext import commands
from discord.ext.commands import BucketType

class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="remindyou")
    @commands.cooldown(1, 10, BucketType.user)  # 1 use per 10 seconds per user
    async def remindyou(self, ctx, member: discord.Member, *, time_input: str):
        """
        Sets a reminder for another user. Accepts both time increments (e.g., '1h30m')
        and specific date/time formats (e.g., '2025-05-10 14:30').
        """
        try:
            # Extract the date/time or time increment from the input
            match = re.match(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2})", time_input)
            if match:
                # Handle specific date/time format
                time_part = match.group(1)  # Extract the matched date/time
                reminder_time = datetime.strptime(time_part, "%Y-%m-%d %H:%M")
                now = datetime.now()
                if reminder_time <= now:
                    await ctx.send("The specified time is in the past. Please provide a future time.")
                    return
                delay = (reminder_time - now).total_seconds()
            else:
                # Handle time increment format
                time_pattern = re.compile(r"((?P<hours>\d+)h)?((?P<minutes>\d+)m)?")
                match = time_pattern.search(time_input)
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
            reminder_message = time_input  # Include the full input as the reminder message
            await ctx.send(f"Reminder set! I'll remind {member.mention} in {time_input}.")
            await discord.utils.sleep_until(datetime.now() + timedelta(seconds=delay))
            await member.send(f"⏰ Reminder from {ctx.author.mention}: {reminder_message}")

        except commands.CommandOnCooldown as e:
            await ctx.send(f"You're using this command too frequently. Try again in {round(e.retry_after, 2)} seconds.")
        except Exception as e:
            await ctx.send(f"An error occurred: {e}")

async def setup(bot):
    await bot.add_cog(Reminders(bot))