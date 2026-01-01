import discord
from discord.ext import commands
from settings import LOG_CHANNEL_ID  # Make sure this exists in your settings file
from datetime import datetime

class Logs(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    async def log_message(self, embed: discord.Embed):
        """Send the log embed to the designated log channel."""
        channel = self.bot.get_channel(LOG_CHANNEL_ID)
        if channel:
            await channel.send(embed=embed)

    # -------------------------
    # Command usage
    @commands.Cog.listener()
    async def on_command(self, ctx: commands.Context):
        embed = discord.Embed(
            title="📝 Command Used",
            colour=discord.Colour.yellow(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="User", value=ctx.author.mention, inline=False)
        embed.add_field(name="Command", value=ctx.command, inline=False)
        embed.add_field(name="Channel", value=ctx.channel.mention, inline=False)
        if ctx.args:
            embed.add_field(name="Arguments", value=" ".join(map(str, ctx.args[1:])), inline=False)
        await self.log_message(embed)

    # -------------------------
    # Member events
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        embed = discord.Embed(
            title="👤 Member Joined",
            description=f"{member.mention} joined the server.",
            colour=discord.Colour.green(),
            timestamp=datetime.utcnow()
        )
        await self.log_message(embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member):
        embed = discord.Embed(
            title="👤 Member Left",
            description=f"{member.mention} left the server.",
            colour=discord.Colour.red(),
            timestamp=datetime.utcnow()
        )
        await self.log_message(embed)

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if before.roles != after.roles:
            embed = discord.Embed(
                title="🔧 Member Roles Updated",
                description=f"{after.mention}'s roles changed.",
                colour=discord.Colour.orange(),
                timestamp=datetime.utcnow()
            )
            embed.add_field(name="Before", value=", ".join([r.name for r in before.roles[1:]]) or "None", inline=False)
            embed.add_field(name="After", value=", ".join([r.name for r in after.roles[1:]]) or "None", inline=False)
            await self.log_message(embed)

    # -------------------------
    # Message events
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.bot:
            return
        embed = discord.Embed(
            title="🗑️ Message Deleted",
            description=f"Author: {message.author.mention}\nChannel: {message.channel.mention}\nContent: {message.content or 'Empty'}",
            colour=discord.Colour.dark_grey(),
            timestamp=datetime.utcnow()
        )
        await self.log_message(embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.author.bot or before.content == after.content:
            return
        embed = discord.Embed(
            title="✏️ Message Edited",
            description=f"Author: {before.author.mention}\nChannel: {before.channel.mention}",
            colour=discord.Colour.orange(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Before", value=before.content or "Empty", inline=False)
        embed.add_field(name="After", value=after.content or "Empty", inline=False)
        await self.log_message(embed)

    # -------------------------
    # Role events
    @commands.Cog.listener()
    async def on_guild_role_create(self, role: discord.Role):
        embed = discord.Embed(
            title="➕ Role Created",
            description=f"Role: {role.name}",
            colour=discord.Colour.green(),
            timestamp=datetime.utcnow()
        )
        await self.log_message(embed)

    @commands.Cog.listener()
    async def on_guild_role_delete(self, role: discord.Role):
        embed = discord.Embed(
            title="➖ Role Deleted",
            description=f"Role: {role.name}",
            colour=discord.Colour.red(),
            timestamp=datetime.utcnow()
        )
        await self.log_message(embed)

    @commands.Cog.listener()
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        embed = discord.Embed(
            title="🔧 Role Updated",
            description=f"Role: {before.name}",
            colour=discord.Colour.orange(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Before", value=f"Name: {before.name}\nColor: {before.color}", inline=False)
        embed.add_field(name="After", value=f"Name: {after.name}\nColor: {after.color}", inline=False)
        await self.log_message(embed)

    # -------------------------
    # Channel events
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        embed = discord.Embed(
            title="➕ Channel Created",
            description=f"Channel: {channel.mention}",
            colour=discord.Colour.green(),
            timestamp=datetime.utcnow()
        )
        await self.log_message(embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        embed = discord.Embed(
            title="➖ Channel Deleted",
            description=f"Channel: {channel.name}",
            colour=discord.Colour.red(),
            timestamp=datetime.utcnow()
        )
        await self.log_message(embed)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        embed = discord.Embed(
            title="🔧 Channel Updated",
            description=f"Channel: {before.name}",
            colour=discord.Colour.orange(),
            timestamp=datetime.utcnow()
        )
        embed.add_field(name="Before", value=f"Name: {before.name}", inline=False)
        embed.add_field(name="After", value=f"Name: {after.name}", inline=False)
        await self.log_message(embed)

    # -------------------------
    # Ban events
    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        embed = discord.Embed(
            title="⛔ Member Banned",
            description=f"{user.mention} was banned.",
            colour=discord.Colour.red(),
            timestamp=datetime.utcnow()
        )
        await self.log_message(embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        embed = discord.Embed(
            title="✅ Member Unbanned",
            description=f"{user.mention} was unbanned.",
            colour=discord.Colour.green(),
            timestamp=datetime.utcnow()
        )
        await self.log_message(embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Logs(bot))
