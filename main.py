import asyncio
import discord
import openai
import os
from discord.ext import commands
from dotenv import load_dotenv
import pathlib
import logging
import uvicorn
import threading
from fastapi import FastAPI, Request
from starlette.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from web_server import app as web_app, BASE_URL, active_flows, CLIENT_SECRETS, SCOPES
from google_services import save_user_credentials

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

# Create FastAPI app
app = web_app  # Use the app from web_server.py

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

# Create a Discord command to start OAuth process
@bot.command(name="connect_google")
async def connect_google(ctx):
    """Connect your Discord account to Google services for personal calendar and tasks"""
    user_id = str(ctx.author.id)
    
    # Ensure the URL has the protocol prefix
    if BASE_URL.startswith(('http://', 'https://')):
        auth_url = f"{BASE_URL}/authorize?user_id={user_id}"
    else:
        auth_url = f"https://{BASE_URL}/authorize?user_id={user_id}"
    
    logger.info(f"Generated auth URL for user {user_id}: {auth_url}")
    await ctx.author.send(f"Click this link to connect your Google account to Discord-Basil:\n{auth_url}")
    await ctx.send("I've sent you a DM with instructions to connect your Google account!")

# Start the Discord bot
async def run_bot():
    logger.info("🚀 Starting Discord bot...")
    await load_cogs()
    await bot.start(os.getenv("DISCORD_BOT_TOKEN"))

# Start the web server
def run_web_server():
    logger.info("🌐 Starting web server...")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

# Main entry point for Railway
if __name__ == "__main__":
    # Check if we're running as the web service or the Discord bot
    is_web = os.environ.get("RAILWAY_SERVICE_NAME", "").lower() == "web"
    
    if is_web:
        # Running as a web service
        logger.info("Starting in web service mode...")
        run_web_server()
    else:
        # Running as the Discord bot with the web server in a thread
        logger.info("Starting in bot+web mode...")
        server_thread = threading.Thread(target=run_web_server, daemon=True)
        server_thread.start()
        asyncio.run(run_bot())
