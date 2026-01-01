import discord
from discord.ext import commands
import logging
import settings  # Import your settings.py

logger = logging.getLogger(__name__)

class Welcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._last_member = None
        self.channel_id = settings.WELCOME_CHANNEL_ID
        logger.info("Welcome cog initialized")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        logger.info(f"New member joined: {member} in guild: {member.guild.name}")

        # Use the channel from settings
        channel = member.guild.get_channel(self.channel_id)
        if channel is not None:
            logger.info(f"Sending welcome message to {member} in {channel.name}")
            await channel.send(f"Welcome to the server, {member.mention}!")
        else:
            logger.warning(
                f"Welcome channel with ID {self.channel_id} not found in guild {member.guild.name}. "
                "Cannot send welcome message."
            )

async def setup(bot: commands.Bot):
    await bot.add_cog(Welcome(bot))
