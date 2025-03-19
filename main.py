import asyncio
import discord
import openai
import os
from discord.ext import commands
from dotenv import load_dotenv
import pathlib
import logging  # Added logging

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("discord")

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True  # Allows access to message content
bot = commands.Bot(command_prefix="!", intents=intents)

# Log when bot is ready
@bot.event
async def on_ready():
    logger.info(f"✅ Logged in as {bot.user}")
    
    # Debug: List all registered commands
    command_list = [cmd.name for cmd in bot.commands]
    logger.info(f"🛠 Registered commands: {command_list}")

# Load all Cogs from the 'commands' directory
async def load_cogs():
    commands_dir = pathlib.Path("commands")
    if commands_dir.exists():
        for command_file in commands_dir.glob("*.py"):
            if command_file.stem != "__init__":  # Avoid loading __init__.py
                module_name = f"commands.{command_file.stem}"
                try:
                    await bot.load_extension(module_name)
                    logger.info(f"✅ Loaded cog: {module_name}")
                except Exception as e:
                    logger.error(f"❌ Failed to load {module_name}: {e}")

# Start the bot
async def run_bot():
    logger.info("🚀 Starting Discord bot...")
    await load_cogs()  # ✅ Load cogs before starting
    await bot.start(os.getenv("DISCORD_BOT_TOKEN"))

if __name__ == "__main__":
    asyncio.run(run_bot())
