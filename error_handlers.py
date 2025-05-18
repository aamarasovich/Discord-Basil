import discord
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

class ErrorHandlers(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        """Handle common command errors"""
        try:
            if isinstance(error, commands.CommandNotFound):
                return
            elif isinstance(error, commands.MissingPermissions):
                await ctx.send("❌ You don't have permission to use this command.")
            elif isinstance(error, commands.BotMissingPermissions):
                await ctx.send("❌ I don't have the required permissions to do that.")
            elif isinstance(error, commands.CommandOnCooldown):
                await ctx.send(f"⏳ Please wait {error.retry_after:.1f}s before using this command again.")
            else:
                logger.error(f"Error in {ctx.command}: {str(error)}")
                await ctx.send("❌ An error occurred while processing your command.")
        except Exception as e:
            logger.error(f"Error in error handler: {str(e)}")

async def setup(bot):
    await bot.add_cog(ErrorHandlers(bot))
