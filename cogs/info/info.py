import discord
import logging
from discord.ext import commands
from settings import BOT_NAME, BOT_AUTHOR

logger = logging.getLogger(__name__)

class Info(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._last_member = None
        logger.info("Info cog initialized")

    @commands.command()
    async def info(self, ctx: commands.Context):
        logger.info(f"Info command used by {ctx.author} in {ctx.guild.name if ctx.guild else 'DM'}")
        info_board = discord.Embed(
            title=BOT_NAME,
            description="This bot has been specially made and designed by Paradym a member of the Nexonix Team",
            colour=discord.Colour.red()
        )
        info_board.set_footer(text=BOT_NAME)
        info_board.set_author(name=BOT_AUTHOR)
        info_board.add_field(name="Commands", value="Type .help for commands.", inline=True)
        await ctx.send(embed=info_board)

    @commands.command()
    async def avatar(self, ctx: commands.Context):
        logger.info(f"Avatar command used by {ctx.author} in {ctx.guild.name if ctx.guild else 'DM'}")
        await ctx.send(ctx.author.display_avatar.url)

    @commands.command()
    async def help(self, ctx: commands.Context):
        """Sends the fun commands help panel with buttons."""
        logger.info(f"Help Help command used by {ctx.author} in {ctx.guild.name if ctx.guild else 'DM'}")
        embed = discord.Embed(
            title="🎮 General Commands",
            colour=discord.Colour.blue(),
            description="Click the buttons below to see command categories."
        )
        embed.set_footer(text="Nexonix Bot Fun Panel")
        await ctx.send(embed=embed, view=FunHelpView(self.bot))

class FunHelpView(discord.ui.View):
    def __init__(self, bot: commands.Bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(label="General Fun", emoji="🎲", style=discord.ButtonStyle.primary, custom_id="fun_general")
    async def general_fun(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🎲 General Fun Commands",
            colour=discord.Colour.green()
        )
        embed.add_field(name=".avatar", value="Shows your avatar.", inline=False)
        embed.add_field(name=".info", value="Info about the bot.", inline=False)
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="Games", emoji="🎮", style=discord.ButtonStyle.primary, custom_id="fun_games")
    async def games(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🎮 Game Commands",
            colour=discord.Colour.purple()
        )
        embed.add_field(name=".coinflip", value="CoinFlip game.", inline=False)
        embed.add_field(name=".writinggame", value="Game for fast writing.", inline=False)
        embed.add_field(name=".minecraft", value="Shows your Minecraft profile.", inline=False)
        embed.add_field(name=".dice <sides>", value="Roll a dice with any number of sides.", inline=False)
        embed.add_field(name=".rate <thing>", value="Rates anything from 0–100.", inline=False)
        embed.add_field(name=".eightball <question>", value="Ask the magic 8Ball a question.", inline=False)
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="Animals", emoji="🐾", style=discord.ButtonStyle.success, custom_id="fun_animals")
    async def animals(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🐾 Animal Commands",
            colour=discord.Colour.teal()
        )
        embed.add_field(name=".cat", value="Sends a random cat picture.", inline=False)
        embed.add_field(name=".dog", value="Sends a random dog picture.", inline=False)
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="Misc / Fun", emoji="✨", style=discord.ButtonStyle.secondary, custom_id="fun_misc")
    async def misc(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="✨ Misc Fun Commands",
            colour=discord.Colour.orange()
        )
        embed.add_field(name=".howgay [user]", value="Shows how gay someone is.", inline=False)
        embed.add_field(name=".smashorpass [user]", value="Decide if you would smash or pass.", inline=False)
        embed.add_field(name=".joke", value="Tells a random joke.", inline=False)
        embed.add_field(name=".wiki <query>", value="Sends wiki link of requested thing.", inline=False)
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="Leveling", emoji="📊", style=discord.ButtonStyle.success, custom_id="fun_leveling")
    async def leveling(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="📊 Leveling Commands",
            colour=discord.Colour.blurple()
        )
        embed.add_field(name=".level [user]", value="Check your or another user's level.", inline=False)
        embed.add_field(name=".rank [user]", value="Shows your rank card.", inline=False)
        embed.add_field(name=".leaderboard", value="Shows the top 10 members.", inline=False)
        await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="Music", emoji="🎵", style=discord.ButtonStyle.primary, custom_id="fun_music")
    async def music(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(
            title="🎵 Music Commands",
            colour=discord.Colour.dark_blue()
        )
        embed.add_field(name=".join", value="Join your voice channel.", inline=False)
        embed.add_field(name=".play <song / URL>", value="Play music from YouTube.", inline=False)
        embed.add_field(name=".pause", value="Pause the current song.", inline=False)
        embed.add_field(name=".resume", value="Resume the song.", inline=False)
        embed.add_field(name=".skip", value="Skip the current song.", inline=False)
        embed.add_field(name=".stop", value="Stop playing and clear the queue.", inline=False)
        embed.add_field(name=".queue", value="Show the current music queue.", inline=False)
        embed.add_field(name=".leave", value="Leave the voice channel.", inline=False)
        await interaction.response.edit_message(embed=embed)



async def setup(bot: commands.Bot):
    await bot.add_cog(Info(bot))
