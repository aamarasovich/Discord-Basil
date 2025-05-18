import discord
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

class BotErrors(commands.Cog):  # ✅ Inherit from commands.Cog
    """Handles centralized error checks and messages for the bot."""

    def __init__(self, bot):
        self.bot = bot  # ✅ Save the bot reference
        super().__init__()  # ✅ Ensure proper Cog initialization

    @staticmethod
    def require_role(role_name: str):
        async def predicate(ctx):
            if ctx.guild is None:  # DM Mode: Skip role checks
                return True
            if discord.utils.get(ctx.author.roles, name=role_name):
                return True
            await ctx.send(f"You must have the `{role_name}` role to use this command.")
            return False
        return commands.check(predicate)

    @staticmethod
    async def handle_error(ctx, error):
        """Handles errors globally and ensures messages are sent via DM first."""
        try:
            dm_channel = await ctx.author.create_dm()
            await dm_channel.send(f"❌ An error occurred while executing the command: {ctx.command}\nError: {error}")
        except discord.Forbidden:
            await ctx.send("❌ An error occurred while executing the command, and I couldn't send you a DM.")

    @commands.command(name="check_oauth")
    @commands.is_owner()
    async def check_oauth(self, ctx):
        """Check the current OAuth configuration."""
        try:
            embed = discord.Embed(
                title="Google OAuth Configuration",
                description="Information about your bot's current OAuth setup",
                color=discord.Color.blue()
            )
            
            # Check if credentials exist
            client_secrets_json = os.getenv("GOOGLE_CREDENTIALS_JSON")
            if not client_secrets_json:
                embed.add_field(
                    name="❌ No OAuth Configuration",
                    value="GOOGLE_CREDENTIALS_JSON environment variable is not set.",
                    inline=False
                )
                await ctx.send(embed=embed)
                return
                
            # Add base URL and redirect URI info
            embed.add_field(
                name="Base URL", 
                value=f"`{BASE_URL}`", 
                inline=False
            )
            
            embed.add_field(
                name="Redirect URI (must be exact in Google Console)", 
                value=f"`{REDIRECT_URI}`", 
                inline=False
            )
            
            # Parse client secrets and show relevant info
            try:
                client_secrets = json.loads(client_secrets_json)
                
                # Client type
                client_type = next(iter(client_secrets.keys()), "unknown")
                embed.add_field(
                    name="Client Type", 
                    value=f"`{client_type}`", 
                    inline=True
                )
                
                # Check if redirect URIs match
                if client_type == 'web' and 'redirect_uris' in client_secrets['web']:
                    redirect_uris = client_secrets['web']['redirect_uris']
                    
                    # Check if our redirect URI is in the configured list
                    if REDIRECT_URI in redirect_uris:
                        embed.add_field(
                            name="✅ Redirect URI Match",
                            value="Your redirect URI is properly configured in Google Cloud Console.",
                            inline=False
                        )
                    else:
                        embed.add_field(
                            name="❌ Redirect URI Mismatch",
                            value=f"Your redirect URI `{REDIRECT_URI}` is **NOT** in the configured list:\n" + 
                                  "\n".join([f"- `{uri}`" for uri in redirect_uris]),
                            inline=False
                        )
                    
                # Project ID
                if client_type == 'web' and 'project_id' in client_secrets['web']:
                    embed.add_field(
                        name="Project ID", 
                        value=f"`{client_secrets['web']['project_id']}`", 
                        inline=True
                    )
                    
                # Add OAuth troubleshooting tips
                embed.add_field(
                    name="📋 Troubleshooting Tips",
                    value=("1. Ensure redirect URI is **exactly** as shown above\n"
                           "2. Add your email as a test user in OAuth consent screen\n"
                           "3. Check that scopes match what's in consent screen\n"
                           "4. Verify app is properly configured as 'External'"),
                    inline=False
                )
                
            except Exception as e:
                embed.add_field(
                    name="❌ Error Parsing Client Secrets", 
                    value=f"Failed to parse client secrets: {str(e)}", 
                    inline=False
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error in check_oauth command: {e}")
            await ctx.send(f"Error checking OAuth configuration: {str(e)}")

# ✅ Properly register the Cog with the bot
async def setup(bot):
    """Required setup function for loading the cog."""
    await bot.add_cog(BotErrors(bot))  # ✅ Pass bot instance to the Cog
