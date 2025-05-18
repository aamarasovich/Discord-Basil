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
    await bot.load_extension('commands.reminders')
    await bot.load_extension('commands.chat')
    await bot.load_extension('commands.user_chat')

async def main():
    """Main entry point"""
    async with bot:
        await load_extensions()
        await bot.start(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    asyncio.run(main())
