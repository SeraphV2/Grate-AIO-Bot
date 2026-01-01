import random
import logging
import discord
from discord.ext import commands
import json
import os
from datetime import datetime

logger = logging.getLogger(__name__)
WARN_FILE = "warnings.json"
LOG_CHANNEL_ID = 123456789012345678  # <-- Replace with your logging channel ID
PRIMARY = discord.Colour.from_rgb(88, 101, 242)  # Discord blurple
SUCCESS = discord.Colour.green()
WARNING = discord.Colour.orange()
DANGER = discord.Colour.red()
GOLD = discord.Colour.gold()

class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        bot.add_view(AdminPanelView())
        logger.info("Admin cog initialized")
        self.warnings = {}
        self.load_warnings()

    # ---------------------------
    # Warning persistence
    def load_warnings(self):
        if os.path.exists(WARN_FILE):
            with open(WARN_FILE, "r") as f:
                self.warnings = json.load(f)
        else:
            self.warnings = {}

    def save_warnings(self):
        with open(WARN_FILE, "w") as f:
            json.dump(self.warnings, f, indent=4)

    # ---------------------------
    # Logging helper
    async def log_action(self, ctx, action: str, target: discord.Member = None, reason: str = None):
        log_channel = ctx.guild.get_channel(LOG_CHANNEL_ID)
        if log_channel is None:
            return

        embed = discord.Embed(
            title="Admin Action Log",
            color=discord.Color.red(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Action", value=action, inline=False)
        embed.add_field(name="By", value=ctx.author.mention, inline=False)

        if target:
            embed.add_field(name="Target", value=target.mention, inline=False)
        if reason:
            embed.add_field(name="Reason / Details", value=reason, inline=False)

        await log_channel.send(embed=embed)

    # ---------------------------
    # Automatic actions based on warnings
    async def auto_action(self, ctx, member: discord.Member):
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)

        warns_count = len(self.warnings[guild_id][user_id])

        # Mute logic removed. Only kick remains.
        if warns_count == 7:
            try:
                await member.kick(reason="Reached 7 warnings")
                await ctx.send(f"⚠️ {member.mention} has been kicked (7 warnings).")
                await self.log_action(ctx, "Kick (7 warnings)", member)
            except:
                await ctx.send(f"❌ Could not kick {member.mention}. Check my permissions.")

    # ---------------------------
    # Warning commands
    @commands.command(name="warn")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def warn(self, ctx, member: discord.Member, *, reason: str = "No reason provided"):
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)

        if guild_id not in self.warnings:
            self.warnings[guild_id] = {}
        if user_id not in self.warnings[guild_id]:
            self.warnings[guild_id][user_id] = []

        self.warnings[guild_id][user_id].append(reason)
        self.save_warnings()

        await ctx.send(f"⚠️ {member.mention} has been warned for: `{reason}`")
        await self.log_action(ctx, "Warn", member, reason)

        try:
            await member.send(f"⚠️ You have been warned in **{ctx.guild.name}** for: `{reason}`")
        except:
            pass

        await self.auto_action(ctx, member)

    @commands.command(name="warnings")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def check_warnings(self, ctx, member: discord.Member):
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)

        if guild_id in self.warnings and user_id in self.warnings[guild_id]:
            warns = self.warnings[guild_id][user_id]

            embed = discord.Embed(
                title=f"Warnings for {member}",
                description="\n".join(f"{i+1}. {reason}" for i, reason in enumerate(warns)),
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"✅ {member.mention} has no warnings.")

    @commands.command(name="clearwarns")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def clear_warnings(self, ctx, member: discord.Member):
        guild_id = str(ctx.guild.id)
        user_id = str(member.id)

        if guild_id in self.warnings and user_id in self.warnings[guild_id]:
            del self.warnings[guild_id][user_id]
            self.save_warnings()

            await ctx.send(f"✅ Warnings for {member.mention} have been cleared.")
            await self.log_action(ctx, "Cleared warnings", member)
        else:
            await ctx.send(f"{member.mention} has no warnings to clear.")


    # ---------------------------
    # Giveaway
    @commands.command()
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def giveaway(self, ctx: commands.Context):
        winner = random.choice(ctx.guild.members)
        await ctx.send(f"🎉 Winner: {winner.mention}")
        await self.log_action(ctx, "Giveaway winner", winner)

    # ---------------------------
    # Ban
    @commands.command(name="ban")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def ban(self, ctx, member: discord.Member, *, reason: str = None):
        bot_member = ctx.guild.me

        if not bot_member.guild_permissions.ban_members:
            return await ctx.send("❌ I don't have `Ban Members` permission.")

        if member == ctx.guild.owner or member == ctx.author:
            return await ctx.send("❌ You cannot ban this user.")

        if (member.top_role >= ctx.author.top_role) and (ctx.author != ctx.guild.owner):
            return await ctx.send("❌ Cannot ban someone with equal or higher role.")

        if member.top_role >= bot_member.top_role:
            return await ctx.send("❌ My role is too low to ban this user.")

        try:
            await member.ban(reason=reason)
            await ctx.send(f"🔨 **{member}** has been banned. Reason: {reason or 'None'}")
            await self.log_action(ctx, "Ban", member, reason)
        except discord.Forbidden:
            await ctx.send("❌ I do not have permission to ban that user.")

    # ---------------------------
    # Kick
    @commands.command(name="kick")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def kick(self, ctx, member: discord.Member, *, reason: str = None):
        bot_member = ctx.guild.me

        if not bot_member.guild_permissions.kick_members:
            return await ctx.send("❌ I don't have `Kick Members` permission.")

        if member == ctx.guild.owner or member == ctx.author:
            return await ctx.send("❌ You cannot kick this user.")

        if (member.top_role >= ctx.author.top_role) and (ctx.author != ctx.guild.owner):
            return await ctx.send("❌ Cannot kick someone with equal or higher role.")

        if member.top_role >= bot_member.top_role:
            return await ctx.send("❌ My role is too low to kick this user.")

        try:
            await member.kick(reason=reason)
            await ctx.send(f"👢 **{member}** has been kicked. Reason: {reason or 'None'}")
            await self.log_action(ctx, "Kick", member, reason)
        except discord.Forbidden:
            await ctx.send("❌ I do not have permission to kick that user.")

    # ---------------------------
    # Lock
    @commands.command(name="lock")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def lock(self, ctx):
        channel = ctx.channel
        overwrite = channel.overwrites_for(ctx.guild.default_role)

        if overwrite.send_messages is False:
            return await ctx.send("🔒 Channel already locked.")

        overwrite.send_messages = False
        await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

        await ctx.send("🔒 **Channel locked.**")
        await self.log_action(ctx, "Lock channel", reason=f"Channel: {channel.name}")

    # ---------------------------
    # Unlock
    @commands.command(name="unlock")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def unlock(self, ctx):
        overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)

        if overwrite.send_messages in (None, True):
            return await ctx.send("🔓 Channel already unlocked.")

        overwrite.send_messages = True
        await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)

        await ctx.send("🔓 **Channel unlocked.**")
        await self.log_action(ctx, "Unlock channel", reason=f"Channel: {ctx.channel.name}")

    # ---------------------------
    # Slowmode
    @commands.command(name="slowmode")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def slowmode(self, ctx, duration: str = None):
        channel = ctx.channel

        if duration is None:
            current = channel.slowmode_delay
            if current == 0:
                return await ctx.send("🕑 Slowmode is **off**.")
            else:
                return await ctx.send(f"🕑 Current slowmode: **{current} seconds**.")

        if duration.lower() in ["off", "disable", "0"]:
            await channel.edit(slowmode_delay=0)
            await ctx.send("🟢 Slowmode disabled.")
            await self.log_action(ctx, "Slowmode disabled", reason=f"Channel: {channel.name}")
            return

        try:
            seconds = int(duration)
            if seconds < 0 or seconds > 21600:
                return await ctx.send("❌ Must be between 0–21600 seconds.")
        except ValueError:
            return await ctx.send("❌ Invalid time. Use a number of seconds.")

        await channel.edit(slowmode_delay=seconds)
        await ctx.send(f"⏳ Slowmode set to **{seconds} seconds**.")
        await self.log_action(ctx, f"Slowmode {seconds}s", reason=f"Channel: {channel.name}")

    # ---------------------------
    # Purge
    @commands.command(name="purge", aliases=["clear"])
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def purge(self, ctx, amount: int = None):
        if not ctx.guild.me.guild_permissions.manage_messages:
            return await ctx.send("❌ I need `Manage Messages` permission.")

        if amount is None:
            deleted = await ctx.channel.purge(limit=None, check=lambda m: not m.pinned)
            await ctx.send(f"🧹 Purged **{len(deleted)}** messages.", delete_after=5)
            await self.log_action(ctx, "Purge entire channel", reason=f"Channel: {ctx.channel.name}")
            return

        if amount <= 0:
            return await ctx.send("❌ Amount must be above 0.")

        deleted = await ctx.channel.purge(limit=amount + 1)
        await ctx.send(f"🧹 Deleted **{len(deleted)-1}** messages.", delete_after=5)
        await self.log_action(ctx, f"Purge {len(deleted)-1}", reason=f"Channel: {ctx.channel.name}")


# -------------------- HELPERS -------------------- #
def cog_loaded(bot: commands.Bot, name: str) -> bool:
    return name in bot.cogs

# =================================================
#                    VIEW
# =================================================
class AdminPanelView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ You must be an administrator to use this panel.",
                ephemeral=True
            )
            return False
        return True

    # ---------------- DASHBOARD ---------------- #
    @discord.ui.button(
        label="Dashboard",
        emoji="🏠",
        style=discord.ButtonStyle.secondary,
        custom_id="admin_dashboard"
    )
    async def dashboard(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild

        embed = discord.Embed(
            title="🧭 Admin Control Panel",
            description="Centralized server management dashboard",
            colour=PRIMARY,
            timestamp=datetime.utcnow()
        )

        embed.add_field(
            name="📊 Server Stats",
            value=(
                f"👥 Members: **{guild.member_count}**\n"
                f"📺 Channels: **{len(guild.channels)}**\n"
                f"🎭 Roles: **{len(guild.roles)}**"
            ),
            inline=False
        )

        embed.add_field(
            name="🧰 Available Systems",
            value=(
                "🛡️ Moderation\n"
                "📺 Channel Control\n"
                "🚨 Anti-Nuke\n"
                "🛡️ Anti-Raid\n"
                "💾 Backups"
            ),
            inline=False
        )

        embed.set_footer(
            text="Nexonix • Premium Server Management",
            icon_url=guild.icon.url if guild.icon else None
        )

        await interaction.response.edit_message(embed=embed, view=self)

    # ---------------- MODERATION ---------------- #
    @discord.ui.button(
        label="Moderation",
        emoji="🛡️",
        style=discord.ButtonStyle.primary,
        custom_id="admin_moderation"
    )
    async def moderation(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🛡️ Moderation Commands",
            colour=DANGER
        )

        embed.add_field(name="Ban", value="`.ban @member <reason>`", inline=False)
        embed.add_field(name="Kick", value="`.kick @member <reason>`", inline=False)
        embed.add_field(name="Warn", value="`.warn @member <reason>`", inline=False)
        embed.add_field(name="Warnings", value="`.warnings @member`", inline=False)
        embed.add_field(name="Clear Warnings", value="`.clearwarns @member`", inline=False)

        await interaction.response.edit_message(embed=embed, view=self)

    # ---------------- CHANNELS ---------------- #
    @discord.ui.button(
        label="Channels",
        emoji="📺",
        style=discord.ButtonStyle.primary,
        custom_id="admin_channels"
    )
    async def channels(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="📺 Channel Control",
            colour=WARNING
        )

        embed.add_field(name="Lock", value="`.lock`", inline=False)
        embed.add_field(name="Unlock", value="`.unlock`", inline=False)
        embed.add_field(name="Slowmode", value="`.slowmode <seconds>` / off", inline=False)
        embed.add_field(name="Purge", value="`.purge <amount>`", inline=False)

        await interaction.response.edit_message(embed=embed, view=self)

    # ---------------- ANTI-NUKE ---------------- #
    @discord.ui.button(
        label="Anti-Nuke",
        emoji="🚨",
        style=discord.ButtonStyle.danger,
        custom_id="admin_antinuke"
    )
    async def antinuke(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🚨 Anti-Nuke System",
            colour=DANGER
        )

        embed.add_field(name="Toggle", value="`.antinuke on|off`", inline=False)
        embed.add_field(name="Status", value="`.anstatus`", inline=False)
        embed.add_field(name="Panic Mode", value="`.panic`", inline=False)
        embed.add_field(name="Owners", value="`.anowners add/remove @user`", inline=False)

        await interaction.response.edit_message(embed=embed, view=self)

    # ---------------- ANTI-RAID ---------------- #
    @discord.ui.button(
        label="Anti-Raid",
        emoji="🛡️",
        style=discord.ButtonStyle.secondary,
        custom_id="admin_antiraid"
    )
    async def antiraid(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🛡️ Anti-Raid Protection",
            colour=PRIMARY
        )

        embed.add_field(name="Enable", value="`.raidenable`", inline=False)
        embed.add_field(name="Disable", value="`.raiddisable`", inline=False)

        await interaction.response.edit_message(embed=embed, view=self)

    # ---------------- BACKUPS ---------------- #
    @discord.ui.button(
        label="Backups",
        emoji="💾",
        style=discord.ButtonStyle.primary,
        custom_id="admin_backups"
    )
    async def backups(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="💾 Server Backups",
            colour=GOLD
        )

        embed.add_field(name="Create Backup", value="`.backup`", inline=False)
        embed.add_field(name="Restore Backup", value="`.restore <id>`", inline=False)
        embed.add_field(name="List Backups", value="`.backups`", inline=False)

        await interaction.response.edit_message(embed=embed, view=self)

    # ---------------- RR ---------------- #
    @discord.ui.button(
        label="Reaction Roles",
        emoji="🎭",
        style=discord.ButtonStyle.primary,
        custom_id="admin_rr"
    )
    async def backups(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🎭 Reaction Roles",
            colour=GOLD
        )

        embed.add_field(name="Send reaction roles to the channel it is executed in", value="`.reactionroles`", inline=False)

        await interaction.response.edit_message(embed=embed, view=self)

class Admin(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        bot.add_view(AdminPanelView(bot))

    @commands.command(name="admin")
    @commands.has_permissions(administrator=True)
    async def admin(self, ctx: commands.Context):
        embed = discord.Embed(
            title="🧭 Admin Control Panel",
            description="Use the buttons below to manage your server",
            colour=PRIMARY,
            timestamp=datetime.utcnow()
        )

        embed.set_footer(
            text="Nexonix • Server Management",
            icon_url=ctx.guild.icon.url if ctx.guild.icon else None
        )

        await ctx.send(embed=embed, view=AdminPanelView(self.bot))

    @admin.error
    async def admin_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("❌ You must be an administrator to use this panel.")




async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
