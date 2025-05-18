import asyncio
import discord
import os
from discord.ext import commands
from dotenv import load_dotenv
import pathlib
import logging
import sys

# Set up logging first, before any other operations
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s: %(message)s'
)
logger = logging.getLogger("discord")

# Load environment variables
load_dotenv()

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

async def load_cogs():
    """Load all cogs with proper error handling"""
    base_dir = pathlib.Path(__file__).parent
    commands_dir = base_dir / "commands"

    # First load error handlers
    try:
        await bot.load_extension('error_handlers')
        logger.info("✅ Loaded error handlers")
    except Exception as e:
        logger.error(f"❌ Failed to load error handlers: {e}")
        return False

    if not commands_dir.exists():
        logger.error(f"❌ Commands directory not found: {commands_dir}")
        return False

    success = True
    for command_file in commands_dir.glob("*.py"):
        if command_file.stem != "__init__":
            module_name = f"commands.{command_file.stem}"
            try:
                await bot.load_extension(module_name)
                logger.info(f"✅ Loaded cog: {module_name}")
            except Exception as e:
                logger.error(f"❌ Failed to load {module_name}: {e}")
                success = False

    return success

def validate_environment():
    """Validate required environment variables before starting"""
    required_vars = {
        "DISCORD_BOT_TOKEN": "Discord bot token",
        "GOOGLE_CREDENTIALS_JSON": "Google service account credentials"
    }
    missing = []
    for var, desc in required_vars.items():
        if not os.getenv(var):
            missing.append(f"{var} ({desc})")
    
    if missing:
        logger.error("Missing required environment variables:")
        for var in missing:
            logger.error(f"- {var}")
        return False
    return True

# Start the Discord bot
async def run_bot():
    """Start the bot with error handling"""
    try:
        logger.info("Starting Discord bot...")
        if not validate_environment():
            sys.exit(1)
            
        if not await load_cogs():
            logger.warning("Some cogs failed to load, but continuing with available commands")
            
        await bot.start(os.getenv("DISCORD_BOT_TOKEN"))
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)

# Main entry point
if __name__ == "__main__":
    asyncio.run(run_bot())
