# fun.py
import random
import discord
from discord.ext import commands

class Fun(commands.Cog):
    """Fun commands!"""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # --------------------------------------------------
    # 8BALL
    # --------------------------------------------------
    @commands.command()
    async def eightball(self, ctx, *, question: str):
        responses = [
            "Yes!", "No!", "Absolutely.", "Definitely not.", "Ask again later...",
            "Without a doubt.", "Very unlikely.", "Trust me—yes.", "No chance.",
            "Maybe… who knows?"
        ]

        embed = discord.Embed(
            title="🎱 8Ball",
            color=discord.Color.random()
        )
        embed.add_field(name="Question", value=question, inline=False)
        embed.add_field(name="Answer", value=random.choice(responses), inline=False)

        await ctx.send(embed=embed)

    # --------------------------------------------------
    # COINFLIP
    # --------------------------------------------------
    @commands.command()
    async def coinflip(self, ctx):
        result = random.choice(["Heads", "Tails"])

        embed = discord.Embed(
            title="🪙 Coin Flip!",
            description=f"**{result}!**",
            color=discord.Color.random()
        )

        await ctx.send(embed=embed)

    # --------------------------------------------------
    # DICE
    # --------------------------------------------------
    @commands.command()
    async def dice(self, ctx, sides: int = 6):
        if sides < 2:
            return await ctx.send("Dice must have at least 2 sides!")

        roll = random.randint(1, sides)

        embed = discord.Embed(
            title="🎲 Dice Roll",
            description=f"You rolled a **{roll}** on a **{sides}-sided** dice!",
            color=discord.Color.random()
        )

        await ctx.send(embed=embed)

    # --------------------------------------------------
    # RATE COMMAND
    # --------------------------------------------------
    @commands.command()
    async def rate(self, ctx, *, thing: str):
        rating = random.randint(0, 100)

        embed = discord.Embed(
            title="⭐ Rating Machine",
            description=f"I rate **{thing}** a **{rating}/100**!",
            color=discord.Color.random()
        )

        await ctx.send(embed=embed)

    # --------------------------------------------------
    # JOKE
    # --------------------------------------------------
    @commands.command()
    async def joke(self, ctx):
        jokes = [
            "Why don’t skeletons fight each other? They don’t have the guts!",
            "I told my computer I needed a break… it said “No problem, I’ll go to sleep.”",
            "Why did the scarecrow win an award? Because he was outstanding in his field!",
            "What do you call fake spaghetti? An impasta!",
            "Parallel lines have so much in common… it’s a shame they’ll never meet."
        ]
        embed = discord.Embed(
            title="😂 Joke Time!",
            description=random.choice(jokes),
            color=discord.Color.random()
        )
        await ctx.send(embed=embed)

    # --------------------------------------------------
    # CAT IMAGE
    # --------------------------------------------------
    @commands.command()
    async def cat(self, ctx):
        images = [
            "https://cataas.com/cat",
            "https://cataas.com/cat/cute",
            "https://cataas.com/cat/says/Meow",
            "https://cataas.com/cat/funny"
        ]
        embed = discord.Embed(
            title="🐱 Cute Cat!",
            color=discord.Color.random()
        )
        embed.set_image(url=random.choice(images))
        await ctx.send(embed=embed)

    # --------------------------------------------------
    # DOG IMAGE
    # --------------------------------------------------
    @commands.command()
    async def dog(self, ctx):
        images = [
            "https://images.dog.ceo/breeds/husky/n02110185_1469.jpg",
            "https://images.dog.ceo/breeds/labrador/n02099712_5642.jpg",
            "https://images.dog.ceo/breeds/shiba/n02085782_9366.jpg"
        ]
        embed = discord.Embed(
            title="🐶 Cute Dog!",
            color=discord.Color.random()
        )
        embed.set_image(url=random.choice(images))
        await ctx.send(embed=embed)

    # --------------------------------------------------
    # HOW GAY
    # --------------------------------------------------
    @commands.command()
    async def howgay(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        percentage = random.randint(0, 100)

        embed = discord.Embed(
            title="🌈 Gay Meter",
            description=f"{user.mention} is **{percentage}% gay** 🏳️‍🌈",
            color=discord.Color.random()
        )
        embed.set_thumbnail(url=user.avatar.url)

        await ctx.send(embed=embed)

    # --------------------------------------------------
    # SMASH OR PASS
    # --------------------------------------------------
    @commands.command()
    async def smashorpass(self, ctx, user: discord.Member = None):
        user = user or ctx.author
        result = random.choice(["🔥 Smash", "❌ Pass"])

        embed = discord.Embed(
            title="😳 Smash or Pass",
            description=f"You chose: **{result}** for {user.mention}",
            color=discord.Color.random()
        )
        embed.set_thumbnail(url=user.avatar.url)

        await ctx.send(embed=embed)

    # --------------------------------------------------
    # FUN COMMAND LIST
    # --------------------------------------------------
    @commands.command(name="fun")
    async def fun_commands(self, ctx):
        embed = discord.Embed(
            title="🎉 Fun Command List",
            description="Here are all fun commands and how to use them:",
            color=discord.Color.blue()
        )

        embed.add_field(
            name=".eightball <question>",
            value="Ask the magic 8Ball a question.",
            inline=False
        )
        embed.add_field(
            name=".coinflip",
            value="Flip a coin — Heads or Tails.",
            inline=False
        )
        embed.add_field(
            name=".dice <sides>",
            value="Roll a dice with any number of sides. Example: `.dice 12`",
            inline=False
        )
        embed.add_field(
            name=".rate <thing>",
            value="Rates anything from 0–100. Example: `.rate pizza`",
            inline=False
        )
        embed.add_field(
            name=".joke",
            value="Tells a random joke.",
            inline=False
        )
        embed.add_field(
            name=".cat",
            value="Sends a random cat picture.",
            inline=False
        )
        embed.add_field(
            name=".dog",
            value="Sends a random dog picture.",
            inline=False
        )
        embed.add_field(
            name=".howgay [user]",
            value="Shows how gay someone is. Example: `.howgay @user`",
            inline=False
        )
        embed.add_field(
            name=".smashorpass [user]",
            value="Decide if you would smash or pass.",
            inline=False
        )

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Fun(bot))
