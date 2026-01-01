import discord
from discord.ext import commands
import time
import json
import os
import logging
from datetime import datetime, timedelta

from settings import ( 
    ANTI_NUKE_ENABLED,
    ANTI_NUKE_OWNERS,
    ANTI_NUKE_LIMITS,
    TIME_WINDOW,
    ANTI_NUKE_PUNISHMENT,
    TIMEOUT_MINUTES,
    PANIC_ROLE_NAME,
    PANIC_CHANNEL_NAME,
    BACKUP_FILE
)

logger = logging.getLogger(__name__)

class AntiNuke(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.actions = {}
        logger.info("Anti-Nuke cog loaded")

    # -------------------------
    # Utilities
    def is_owner(self, user_id: int):
        return user_id in ANTI_NUKE_OWNERS

    def track(self, guild_id: int, user_id: int, action: str):
        now = time.time()
        self.actions.setdefault(guild_id, {}).setdefault(user_id, {}).setdefault(action, [])
        self.actions[guild_id][user_id][action].append(now)

        # cleanup
        self.actions[guild_id][user_id][action] = [
            t for t in self.actions[guild_id][user_id][action]
            if now - t <= TIME_WINDOW
        ]

        return len(self.actions[guild_id][user_id][action])

    async def get_executor(self, guild: discord.Guild, action):
        try:
            async for entry in guild.audit_logs(limit=1, action=action):
                return entry.user
        except Exception as e:
            logger.error("Audit log error", exc_info=e)
        return None

    async def punish(self, guild: discord.Guild, member: discord.Member):
        if self.is_owner(member.id):
            return

        try:
            if ANTI_NUKE_PUNISHMENT == "ban":
                await member.ban(reason="Anti-Nuke Triggered")
            elif ANTI_NUKE_PUNISHMENT == "kick":
                await member.kick(reason="Anti-Nuke Triggered")
            else:
                until = datetime.utcnow() + timedelta(minutes=TIMEOUT_MINUTES)
                await member.edit(timed_out_until=until, reason="Anti-Nuke Triggered")
        except:
            pass

    # -------------------------
    # Backup
    @commands.command(name="backup")
    @commands.has_permissions(administrator=True)
    async def backup(self, ctx):
        data = {
            "roles": [],
            "channels": []
        }

        for role in ctx.guild.roles:
            if role.is_default():
                continue
            data["roles"].append({
                "name": role.name,
                "permissions": role.permissions.value,
                "color": role.color.value,
                "hoist": role.hoist,
                "mentionable": role.mentionable
            })

        for ch in ctx.guild.channels:
            data["channels"].append({
                "name": ch.name,
                "type": ch.type.name,
                "category": ch.category.name if ch.category else None
            })

        with open(BACKUP_FILE, "w") as f:
            json.dump(data, f, indent=4)

        await ctx.send("📦 Server backup saved.")

    async def restore(self, guild: discord.Guild):
        if not os.path.exists(BACKUP_FILE):
            return

        with open(BACKUP_FILE) as f:
            data = json.load(f)

        for r in data["roles"]:
            await guild.create_role(
                name=r["name"],
                permissions=discord.Permissions(r["permissions"]),
                color=discord.Color(r["color"]),
                hoist=r["hoist"],
                mentionable=r["mentionable"]
            )

        for c in data["channels"]:
            await guild.create_text_channel(c["name"])

    # -------------------------
    # Panic Mode
    @commands.command(name="panic")
    @commands.has_permissions(administrator=True)
    async def panic(self, ctx):
        role = discord.utils.get(ctx.guild.roles, name=PANIC_ROLE_NAME)
        if not role:
            role = await ctx.guild.create_role(name=PANIC_ROLE_NAME)

        for channel in ctx.guild.channels:
            await channel.set_permissions(
                ctx.guild.default_role,
                send_messages=False,
                connect=False
            )

        await ctx.send("🚨 PANIC MODE ACTIVATED")

    # -------------------------
    # Status
    @commands.command(name="antinuke")
    async def antinuke(self, ctx):
        embed = discord.Embed(
            title="🛡️ Anti-Nuke Status",
            color=discord.Color.red()
        )
        embed.add_field(name="Enabled", value=ANTI_NUKE_ENABLED)
        embed.add_field(name="Owners Immune", value=len(ANTI_NUKE_OWNERS))
        embed.add_field(name="Punishment", value=ANTI_NUKE_PUNISHMENT)
        embed.add_field(name="Time Window", value=f"{TIME_WINDOW}s")
        await ctx.send(embed=embed)

    # -------------------------
    # EVENTS
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        if not ANTI_NUKE_ENABLED:
            return

        executor = await self.get_executor(channel.guild, discord.AuditLogAction.channel_delete)
        if not executor or self.is_owner(executor.id):
            return

        count = self.track(channel.guild.id, executor.id, "channel_delete")
        if count >= ANTI_NUKE_LIMITS["channel_delete"]:
            member = channel.guild.get_member(executor.id)
            if member:
                await self.punish(channel.guild, member)
                await self.restore(channel.guild)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        if not ANTI_NUKE_ENABLED:
            return

        executor = await self.get_executor(role.guild, discord.AuditLogAction.role_delete)
        if not executor or self.is_owner(executor.id):
            return

        count = self.track(role.guild.id, executor.id, "role_delete")
        if count >= ANTI_NUKE_LIMITS["role_delete"]:
            member = role.guild.get_member(executor.id)
            if member:
                await self.punish(role.guild, member)
                await self.restore(role.guild)

    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        if not ANTI_NUKE_ENABLED:
            return

        executor = await self.get_executor(after, discord.AuditLogAction.guild_update)
        if not executor or self.is_owner(executor.id):
            return

        count = self.track(after.id, executor.id, "guild_update")
        if count >= ANTI_NUKE_LIMITS["guild_update"]:
            member = after.get_member(executor.id)
            if member:
                await self.punish(after, member)

async def setup(bot: commands.Bot):
    await bot.add_cog(AntiNuke(bot))
