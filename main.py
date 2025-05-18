import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# Load commands
async def load_cogs():
    await bot.load_extension('commands.reminders')

# Main entry point
if __name__ == "__main__":
    bot.loop.run_until_complete(load_cogs())
    bot.run(os.getenv("DISCORD_TOKEN"))
