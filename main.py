import asyncio
import discord
import openai
import os
from discord.ext import commands
from dotenv import load_dotenv
import pathlib
import logging  # Added logging
import uvicorn
import threading
from web_server import app, BASE_URL

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
    
    # Log OAuth information
    logger.info(f"🔗 OAuth Redirect URI for Google Console setup: {BASE_URL}/oauth2callback")
    logger.info("ℹ️ Make sure to add this URI to your Google Cloud Console's Authorized redirect URIs")
    
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
    logger.info("🚀 Starting Discord bot...")
    await load_cogs()  # ✅ Load cogs before starting
    await bot.start(os.getenv("DISCORD_BOT_TOKEN"))

# Start the web server
def run_web_server():
    logger.info("🌐 Starting web server...")
    port = int(os.getenv("PORT", 8000))  # Use PORT env var or default to 8000
    uvicorn.run(app, host="0.0.0.0", port=port)

# Create a Discord command to start OAuth process
@bot.command(name="connect_google")
async def connect_google(ctx):
    """Connect your Discord account to Google services for personal calendar and tasks"""
    user_id = str(ctx.author.id)
    base_url = os.getenv("BASE_URL", "http://localhost:8000")  # Get the base URL from env or use default
    auth_url = f"{base_url}/authorize?user_id={user_id}"
    
    await ctx.author.send(f"Click this link to connect your Google account to Discord-Basil:\n{auth_url}")
    await ctx.send("I've sent you a DM with instructions to connect your Google account!")

if __name__ == "__main__":
    # Start the web server in a separate thread
    server_thread = threading.Thread(target=run_web_server, daemon=True)
    server_thread.start()
    
    # Start the bot in the main thread
    asyncio.run(run_bot())
