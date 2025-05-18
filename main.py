import discord
import asyncio
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

async def load_extensions():
    """Load all command extensions"""
    extensions = {
        'commands.reminders': True,  # Required
        'commands.chat': False,      # Optional
        'commands.user_chat': False  # Optional
    }
    
    for ext, required in extensions.items():
        try:
            await bot.load_extension(ext)
            print(f"✅ Loaded extension: {ext}")
        except Exception as e:
            print(f"{'❌' if required else '⚠️'} {ext}: {str(e)}")
            if required:
                raise  # Re-raise if this was a required extension

async def main():
    """Main entry point"""
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise ValueError("DISCORD_TOKEN not found in environment variables")
        
    async with bot:
        await load_extensions()
        await bot.start(token)

if __name__ == "__main__":
    asyncio.run(main())
