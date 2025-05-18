import discord
from discord.ext import commands
from discord.ext.commands import BucketType
import re
from datetime import datetime, timedelta

class Reminders(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="remindyou")
    @commands.cooldown(1, 10, BucketType.user)
    async def remindyou(self, ctx, member: discord.Member = None, *, time_input: str = None):
        """Sets a reminder for another user."""
        if not member:
            await ctx.send("You need to mention a user to remind! Example: `!remindyou @JohnDoe 1h30m Check the oven`")
            return
        if not time_input:
            await ctx.send("You need to specify a time and message! Example: `!remindyou @JohnDoe 1h30m Check the oven`")
            return

        try:
            time_pattern = re.compile(r"((?P<hours>\d+)h)?((?P<minutes>\d+)m)?")
            match = time_pattern.search(time_input)
            
            if not match:
                await ctx.send("Invalid time format. Use format like '1h30m'")
                return
                
            time_data = match.groupdict()
            hours = int(time_data['hours']) if time_data['hours'] else 0
            minutes = int(time_data['minutes']) if time_data['minutes'] else 0
            
            if hours == 0 and minutes == 0:
                await ctx.send("Please specify a valid time (e.g., 1h30m)")
                return
                
            delay = timedelta(hours=hours, minutes=minutes)
            reminder_time = datetime.now() + delay
            
            # Remove the time part from the message
            reminder_message = time_input[match.end():].strip()
            if not reminder_message:
                reminder_message = "Reminder!"
                
            await ctx.send(f"✅ I will remind {member.mention} in {hours}h{minutes}m")
            
            # Wait for the specified time
            await discord.utils.sleep_until(reminder_time)
            
            # Send the reminder
            try:
                await member.send(f"⏰ Reminder from {ctx.author.mention}: {reminder_message}")
            except discord.Forbidden:
                await ctx.send(f"I couldn't send a DM to {member.mention}. They might have DMs disabled.")
                
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

async def setup(bot):
    await bot.add_cog(Reminders(bot))