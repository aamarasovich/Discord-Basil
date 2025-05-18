import discord
import asyncio
from discord.ext import commands, tasks
from discord.ext.commands import BucketType, CommandOnCooldown
import os
from dotenv import load_dotenv

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# A function to convert time strings to seconds
def convert_time_to_seconds(time_str):
    try:
        # If the time string is in the format "1h30m", "2d", "45s", etc.
        if 'h' in time_str:
            hours = int(time_str.split('h')[0])
            minutes = int(time_str.split('h')[1].replace('m', ''))
            return hours * 3600 + minutes * 60
        elif 'd' in time_str:
            days = int(time_str.split('d')[0])
            return days * 86400
        elif 'm' in time_str:
            minutes = int(time_str.split('m')[0])
            return minutes * 60
        elif 's' in time_str:
            seconds = int(time_str.split('s')[0])
            return seconds
        else:
            return None
    except Exception as e:
        return None

async def set_reminder(ctx, target: discord.Member, time: str, reminder: str):
    """Shared reminder logic for all reminder commands"""
    seconds = convert_time_to_seconds(time)
    if seconds is None:
        await ctx.send("Invalid time format. Please use format like '1h30m', '2d', '45s', etc.")
        return False
    
    @tasks.loop(count=1)
    async def reminder_task():
        await asyncio.sleep(seconds)
        await ctx.send(f"{target.mention} Reminder: {reminder}")
        
    reminder_task.start()
    return True

# A command to set a reminder
@bot.command()
@commands.cooldown(1, 60, BucketType.user)  # 1 use per 60 seconds per user
async def remind(ctx, time: str, *, reminder: str):
    """Alias for remindme"""
    await remindme(ctx, time, reminder=reminder)

@bot.command()
@commands.cooldown(1, 60, BucketType.user)  # 1 use per 60 seconds per user
async def remindme(ctx, time: str, *, reminder: str):
    try:
        if await set_reminder(ctx, ctx.author, time, reminder):
            await ctx.send(f"I'll remind you about '{reminder}' in {time}")
    except Exception as e:
        await ctx.send(f"Error setting reminder: {str(e)}")

@bot.command()
@commands.cooldown(1, 60, BucketType.user)  # 1 use per 60 seconds per user
async def remindyou(ctx, member: discord.Member, time: str, *, reminder: str):
    try:
        if await set_reminder(ctx, member, time, reminder):
            await ctx.send(f"Reminder set for {member.mention}: '{reminder}' in {time}")
    except Exception as e:
        await ctx.send(f"Error setting reminder: {str(e)}")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, CommandOnCooldown):
        remaining = round(error.retry_after)
        await ctx.send(f"Please wait {remaining} seconds before using this command again.")
    else:
        raise error

# An event that is called when the bot has connected to Discord and is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    # Change the bot's status to "online"
    await bot.change_presence(status=discord.Status.online)

async def main():
    TOKEN = os.getenv('DISCORD_TOKEN')
    await bot.start(TOKEN)

if __name__ == "__main__":
    load_dotenv()
    asyncio.run(main())