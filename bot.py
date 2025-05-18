import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timedelta
import pytz
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the Discord bot token from the environment variables
TOKEN = os.getenv('DISCORD_TOKEN')

# Intents are used to specify which events the bot should receive
intents = discord.Intents.default()
intents.messages = True

# Create an instance of the bot with the specified command prefix and intents
bot = commands.Bot(command_prefix='!', intents=intents)

# A dictionary to store reminders for each user
reminders = {}

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

# A command to set a reminder
@bot.command()
async def remind(ctx, time: str, *, reminder: str):
    try:
        # Convert time string to seconds
        seconds = convert_time_to_seconds(time)
        if seconds is None:
            await ctx.send("Invalid time format. Please use format like '1h30m', '2d', '45s', etc.")
            return
        
        # Set reminder
        await ctx.send(f"Reminder set for {ctx.author.mention}: '{reminder}' in {time}")
        await asyncio.sleep(seconds)
        await ctx.send(f"{ctx.author.mention} Reminder: {reminder}")
        
    except Exception as e:
        await ctx.send(f"Error setting reminder: {str(e)}")

@bot.command()
async def remindme(ctx, time: str, *, reminder: str):
    try:
        # Convert time string to seconds
        seconds = convert_time_to_seconds(time)
        if seconds is None:
            await ctx.send("Invalid time format. Please use format like '1h30m', '2d', '45s', etc.")
            return
        
        # Set reminder
        await ctx.send(f"I'll remind you about '{reminder}' in {time}")
        await asyncio.sleep(seconds)
        await ctx.send(f"{ctx.author.mention} Reminder: {reminder}")
        
    except Exception as e:
        await ctx.send(f"Error setting reminder: {str(e)}")

# An event that is called when the bot has connected to Discord and is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    # Change the bot's status to "online"
    await bot.change_presence(status=discord.Status.online)

# Run the bot with the specified token
bot.run(TOKEN)