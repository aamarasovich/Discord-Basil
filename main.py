import discord
import asyncio
from discord.ext import commands
import os
from dotenv import load_dotenv
import logging

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
    print(f"✅ Logged in as {bot.user}")

@bot.event
async def on_error(event, *args, **kwargs):
    print(f"❌ Error in {event}: {args} {kwargs}")

async def load_extensions():
    """Load all command extensions"""
    # Only load reminders for now
    try:
        await bot.load_extension('commands.reminders')
        print("✅ Loaded reminders extension")
    except Exception as e:
        print(f"❌ Error loading reminders: {e}")
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
                logger.info("🔄 Connecting to Discord...")
                await load_extensions()
                logger.debug("Starting bot with token...")
                await bot.start(token)
        except discord.errors.LoginFailure as e:
            logger.error(f"Authentication Failed: {str(e)}")
            logger.error(f"Token type: {type(token)}")
            logger.error(f"Environment source: {'Environment' if token in os.environ else '.env file'}")
            raise  # Re-raise to stop the bot
        except Exception as e:
            logger.error(f"❌ Fatal error: {str(e)}", exc_info=True)
            await asyncio.sleep(5)
        finally:
            logger.warning("⚠️ Bot disconnected. Attempting to reconnect in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
