import asyncio
import discord
import openai
import os
from discord.ext import commands
from dotenv import load_dotenv
import pathlib
import logging

# Set up logging first, before any other operations
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s: %(message)s'
)
logger = logging.getLogger("discord")

# Load environment variables
load_dotenv()

# Initialize OpenAI client
openai_client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
    # Ensure we use an absolute path to locate the 'commands' directory
    base_dir = pathlib.Path(__file__).parent
    commands_dir = base_dir / "commands"

    if commands_dir.exists():
        for command_file in commands_dir.glob("*.py"):
            if command_file.stem != "__init__":  # Avoid loading __init__.py
                module_name = f"commands.{command_file.stem}"
                try:
                    await bot.load_extension(module_name)
                    logger.info(f"✅ Loaded cog: {module_name}")
                except Exception as e:
                    logger.error(f"❌ Failed to load {module_name}: {e}")
    else:
        logger.error(f"❌ Commands directory not found: {commands_dir}")

# Start the Discord bot
async def run_bot():
    logger.info("Starting Discord bot...")
    await bot.load_extension('error_handlers')  # Load error handlers first
    await load_cogs()  # Then load other cogs
    await bot.start(os.getenv("DISCORD_BOT_TOKEN"))

# Main entry point
if __name__ == "__main__":
    asyncio.run(run_bot())
