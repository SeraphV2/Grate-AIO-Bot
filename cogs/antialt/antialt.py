import discord
from discord.ext import commands
from datetime import datetime, timedelta
from collections import deque
import logging
import settings

logger = logging.getLogger(__name__)

class AntiAltRaid(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.recent_joins = {}  # guild_id: deque of join times
        self.anti_alt_enabled = settings.ANTI_ALT_ENABLED
        self.anti_raid_enabled = settings.ANTI_RAID_ENABLED

    # ---------------------------
    # Anti-Alt check
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        # Admin bypass
        if member.id in settings.ADMIN_IDS:
            return

        if self.anti_alt_enabled:
            account_age = (datetime.utcnow() - member.created_at).days
            if account_age < settings.ANTI_ALT_MIN_ACCOUNT_AGE:
                try:
                    action = settings.ANTI_ALT_ACTION
                    if action == "kick":
                        await member.kick(reason="Anti-Alt: account too new")
                    elif action == "ban":
                        await member.ban(reason="Anti-Alt: account too new")
                    logger.info(f"{action.capitalize()}ed {member} for alt account ({account_age} days old)")
                except Exception as e:
                    logger.error(f"Failed to take action on alt account {member}: {e}")

        if self.anti_raid_enabled:
            await self.track_join(member)

    # ---------------------------
    # Track joins for anti-raid
    async def track_join(self, member: discord.Member):
        guild_id = member.guild.id
        if guild_id not in self.recent_joins:
            self.recent_joins[guild_id] = deque()

        now = datetime.utcnow()
        self.recent_joins[guild_id].append(now)

        # remove old timestamps
        timeframe = timedelta(seconds=settings.ANTI_RAID_TIME_FRAME)
        while self.recent_joins[guild_id] and now - self.recent_joins[guild_id][0] > timeframe:
            self.recent_joins[guild_id].popleft()

        if len(self.recent_joins[guild_id]) > settings.ANTI_RAID_MAX_JOIN_RATE:
            await self.handle_raid(member.guild)

    # ---------------------------
    # Handle raid
    async def handle_raid(self, guild: discord.Guild):
        action = settings.RAID_ACTION
        for member in guild.members:
            if member.id in settings.ADMIN_IDS:
                continue

            try:
                if action == "kick":
                    await member.kick(reason="Anti-Raid: detected raid join")
                elif action == "ban":
                    await member.ban(reason="Anti-Raid: detected raid join")
            except Exception as e:
                logger.error(f"Failed to {action} {member} during raid protection: {e}")

        logger.warning(f"Anti-Raid triggered in {guild.name}, action: {action}")

    # ---------------------------
    # Admin commands
    @commands.group(name="antiraid", invoke_without_command=True)
    @commands.has_permissions(administrator=True)
    async def antiraid(self, ctx):
        embed = discord.Embed(title="Anti-Alt / Raid Status", color=discord.Color.blue())
        embed.add_field(name="Anti-Alt", value=f"{'Enabled' if self.anti_alt_enabled else 'Disabled'}", inline=False)
        embed.add_field(name="Anti-Raid", value=f"{'Enabled' if self.anti_raid_enabled else 'Disabled'}", inline=False)
        await ctx.send(embed=embed)

    @antiraid.command(name="enable")
    @commands.has_permissions(administrator=True)
    async def enable(self, ctx, system: str):
        if system.lower() == "alt":
            self.anti_alt_enabled = True
            await ctx.send("✅ Anti-Alt system enabled.")
        elif system.lower() == "raid":
            self.anti_raid_enabled = True
            await ctx.send("✅ Anti-Raid system enabled.")
        else:
            await ctx.send("❌ Invalid system. Use `alt` or `raid`.")

    @antiraid.command(name="disable")
    @commands.has_permissions(administrator=True)
    async def disable(self, ctx, system: str):
        if system.lower() == "alt":
            self.anti_alt_enabled = False
            await ctx.send("✅ Anti-Alt system disabled.")
        elif system.lower() == "raid":
            self.anti_raid_enabled = False
            await ctx.send("✅ Anti-Raid system disabled.")
        else:
            await ctx.send("❌ Invalid system. Use `alt` or `raid`.")

async def setup(bot: commands.Bot):
    await bot.add_cog(AntiAltRaid(bot))
