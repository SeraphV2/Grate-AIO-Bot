import discord
from discord.ext import commands
import logging
import settings  # Import your settings.py

logger = logging.getLogger(__name__)

class Welcome(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.channel_id = settings.WELCOME_CHANNEL_ID
        self.message_template = getattr(settings, "WELCOME_MESSAGE", "Welcome {member} to {server}! 🎉")
        logger.info("Welcome cog initialized")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        logger.info(f"New member joined: {member} in guild: {member.guild.name}")

        # Get the channel
        channel = member.guild.get_channel(self.channel_id)
        if not channel:
            logger.warning(
                f"Welcome channel with ID {self.channel_id} not found in guild {member.guild.name}. "
                "Cannot send welcome message."
            )
            return

        # Create an embed welcome message
        embed = discord.Embed(
            title="🎉 Welcome!",
            description=self.message_template.format(member=member.mention, server=member.guild.name),
            color=discord.Colour.green(),
            timestamp=member.joined_at
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.set_footer(text=f"{member.guild.name} • Enjoy your stay!")

        await channel.send(embed=embed)
        logger.info(f"Welcome message sent to {member} in {channel.name}")


async def setup(bot: commands.Bot):
    await bot.add_cog(Welcome(bot))
