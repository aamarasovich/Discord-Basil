import discord
import asyncio
from discord.ext import commands
import os
from dotenv import load_dotenv
import logging
import sys

# Fix Windows console encoding for Unicode
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)

# Load environment variables
load_dotenv()

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"[OK] Logged in as {bot.user}")

@bot.event
async def on_error(event, *args, **kwargs):
    print(f"[ERROR] Error in {event}: {args} {kwargs}")

async def load_extensions():
    """Load all command extensions"""
    # Only load reminders for now
    try:
        # Check if extension is already loaded
        if 'commands.reminders' in bot.extensions:
            print("[INFO] Reminders extension already loaded")
        else:
            await bot.load_extension('commands.reminders')
            print("[OK] Loaded reminders extension")
    except discord.ext.commands.errors.ExtensionAlreadyLoaded:
        print("[INFO] Reminders extension already loaded")
    except Exception as e:
        print(f"[ERROR] Error loading reminders: {e}")
        raise  # Re-raise since reminders are essential

async def main():
    """Main entry point"""
    token = os.getenv("DISCORD_TOKEN")
    
    # Debug token presence and format
    logger.debug(f"Token exists: {bool(token)}")
    if token:
        logger.debug(f"Token length: {len(token)}")
        logger.debug(f"Token prefix: {token[:7]}...")  # Only show first few chars for security
    else:
        logger.error("NO TOKEN FOUND IN ENVIRONMENT!")
        logger.debug(f"Available env vars: {[k for k in os.environ.keys()]}")
    
    while True:
        try:
            async with bot:
                logger.info("[INFO] Connecting to Discord...")
                await load_extensions()
                logger.debug("Starting bot with token...")
                await bot.start(token)
        except discord.errors.LoginFailure as e:
            logger.error(f"Authentication Failed: {str(e)}")
            logger.error(f"Token type: {type(token)}")
            logger.error(f"Environment source: {'Environment' if token in os.environ else '.env file'}")
            raise  # Re-raise to stop the bot
        except Exception as e:
            logger.error(f"[ERROR] Fatal error: {str(e)}", exc_info=True)
            await asyncio.sleep(5)
        finally:
            logger.warning("[WARNING] Bot disconnected. Attempting to reconnect in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
