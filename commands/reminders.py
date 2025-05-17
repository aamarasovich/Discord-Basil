import re
from datetime import datetime, timedelta
import discord
from discord.ext import commands
from discord.ext.commands import BucketType
import dateparser
from ..config import TIMEZONE, COOLDOWN_DURATION

class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def parse_time(self, time_input: str) -> tuple[datetime, str]:
        """Parse various time formats and return datetime object and format used"""
        # Try existing increment format (1h30m)
        time_pattern = re.compile(r"((?P<hours>\d+)h)?((?P<minutes>\d+)m)?")
        inc_match = time_pattern.search(time_input)
        if inc_match and (inc_match.group('hours') or inc_match.group('minutes')):
            hours = int(inc_match.group('hours') or 0)
            minutes = int(inc_match.group('minutes') or 0)
            return datetime.now() + timedelta(hours=hours, minutes=minutes), "increment"

        # Try dateparser for natural language
        settings = {
            'TIMEZONE': str(TIMEZONE),
            'RETURN_AS_TIMEZONE_AWARE': True,
            'PREFER_DATES_FROM': 'future'
        }
        parsed_date = dateparser.parse(time_input, settings=settings)
        if parsed_date:
            return parsed_date, "natural"

        raise ValueError("Could not parse time format")

    @commands.command(name="remindme")
    @commands.cooldown(1, COOLDOWN_DURATION, BucketType.user)
    async def remindme(self, ctx, *, time_input: str):
        """
        Sets a reminder. Examples:
        !remindme 1h30m check email
        !remindme may 18 10am doctor appointment
        !remindme tomorrow 3pm call mom
        !remindme 6-6 1800 team meeting
        """
        try:
            # Split time and message
            parts = time_input.split(maxsplit=1)
            time_str = parts[0]
            message = parts[1] if len(parts) > 1 else "Reminder!"
            
            if len(parts) > 1:
                # Try parsing with potential second time part (e.g., "may 18 10am")
                try:
                    reminder_time, format_used = self.parse_time(f"{parts[0]} {parts[1].split()[0]}")
                    message = " ".join(parts[1].split()[1:]) or "Reminder!"
                except:
                    reminder_time, format_used = self.parse_time(parts[0])
            else:
                reminder_time, format_used = self.parse_time(time_str)

            now = datetime.now(TIMEZONE)
            if reminder_time <= now:
                await ctx.send("⚠️ The specified time is in the past. Please provide a future time.")
                return

            delay = (reminder_time - now).total_seconds()
            readable_time = reminder_time.strftime("%B %d at %I:%M %p")
            
            await ctx.send(f"✅ Reminder set for {readable_time}!\nI'll remind you: {message}")
            await discord.utils.sleep_until(reminder_time)
            await ctx.author.send(f"⏰ Reminder: {message}")

        except ValueError as ve:
            await ctx.send("❌ Invalid time format. Try examples like:\n"
                         "• `1h30m`\n"
                         "• `may 18 10am`\n"
                         "• `tomorrow 3pm`\n"
                         "• `6-6 1800`")
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

async def setup(bot):
    await bot.add_cog(Reminders(bot))