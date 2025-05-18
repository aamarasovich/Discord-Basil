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
    if not token:
        raise ValueError("DISCORD_TOKEN not found in environment variables")
    
    while True:
        try:
            async with bot:
                print("🔄 Connecting to Discord...")
                await load_extensions()
                await bot.start(token)
        except discord.errors.ConnectionClosed:
            print("🔌 Connection closed. Attempting to reconnect...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f"❌ Fatal error: {str(e)}")
            raise
        finally:
            print("⚠️ Bot disconnected. Attempting to reconnect in 5 seconds...")
            await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
