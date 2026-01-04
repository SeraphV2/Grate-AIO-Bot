import discord
from discord.ext import commands, tasks
import json
import os
import time
from PIL import Image, ImageDraw, ImageFont

from settings import *

LEVELS_FILE = "levels.json"


def load_levels():
    if not os.path.exists(LEVELS_FILE):
        with open(LEVELS_FILE, "w") as f:
            json.dump({}, f)
        return {}

    with open(LEVELS_FILE, "r") as f:
        return json.load(f)


def save_levels(data):
    with open(LEVELS_FILE, "w") as f:
        json.dump(data, f, indent=4)


def xp_for_next_level(level):
    return 100 + (level * 75)


class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.levels = load_levels()
        self.text_cooldowns = {}
        self.voice_tracker = {}
        self.voice_xp.start()

    def get_user(self, guild_id, user_id):
        self.levels.setdefault(guild_id, {})
        self.levels[guild_id].setdefault(user_id, {
            "xp": 0,
            "level": 0,
            "prestige": 0
        })
        return self.levels[guild_id][user_id]

    async def handle_level_roles(self, member, level):
        for req_level, role_id in LEVEL_ROLES.items():
            role = member.guild.get_role(role_id)
            if not role:
                continue

            if level >= req_level and role not in member.roles:
                await member.add_roles(role)

            if REMOVE_OLD_LEVEL_ROLES and level < req_level and role in member.roles:
                await member.remove_roles(role)

    async def handle_prestige(self, member, data):
        if not PRESTIGE_ENABLED:
            return

        if data["level"] >= PRESTIGE_LEVEL_REQUIREMENT:
            data["level"] = 0
            data["xp"] = 0
            data["prestige"] += 1

            role = member.guild.get_role(PRESTIGE_ROLE_ID)
            if role:
                await member.add_roles(role)

            await member.send(f"🌟 You prestiged! Prestige level **{data['prestige']}**")

    @commands.Cog.listener()
    async def on_message(self, message):
        if not LEVELING_ENABLED or message.author.bot or not message.guild:
            return

        now = time.time()
        uid = str(message.author.id)
        gid = str(message.guild.id)

        if now - self.text_cooldowns.get(uid, 0) < TEXT_XP_COOLDOWN:
            return

        self.text_cooldowns[uid] = now
        data = self.get_user(gid, uid)

        data["xp"] += int(TEXT_XP_PER_MESSAGE * LEVEL_XP_MULTIPLIER)

        needed = xp_for_next_level(data["level"])
        if data["xp"] >= needed:
            data["xp"] -= needed
            data["level"] += 1

            await self.handle_level_roles(message.author, data["level"])
            await self.handle_prestige(message.author, data)

            channel = (
                self.bot.get_channel(LEVEL_UP_CHANNEL_ID)
                if LEVEL_UP_CHANNEL_ID else message.channel
            )

            await channel.send(
                LEVEL_UP_MESSAGE.format(
                    member=message.author.mention,
                    level=data["level"]
                )
            )

        save_levels(self.levels)

    # ---------------- VOICE XP ---------------- #

    @tasks.loop(seconds=VOICE_XP_CHECK_INTERVAL)
    async def voice_xp(self):
        if not LEVELING_ENABLED:
            return

        for guild in self.bot.guilds:
            for vc in guild.voice_channels:
                for member in vc.members:
                    if member.bot:
                        continue

                    gid = str(guild.id)
                    uid = str(member.id)
                    data = self.get_user(gid, uid)

                    data["xp"] += VOICE_XP_PER_MINUTE

                    needed = xp_for_next_level(data["level"])
                    if data["xp"] >= needed:
                        data["xp"] -= needed
                        data["level"] += 1
                        await self.handle_level_roles(member, data["level"])
                        await self.handle_prestige(member, data)

        save_levels(self.levels)

    # ---------------- COMMANDS ---------------- #

    @commands.command()
    async def level(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        data = self.get_user(str(ctx.guild.id), str(member.id))

        await ctx.send(
            f"📊 **{member.display_name}**\n"
            f"Level: **{data['level']}**\n"
            f"XP: **{data['xp']}** / {xp_for_next_level(data['level'])}\n"
            f"Prestige: **{data['prestige']}**"
        )

    @commands.command()
    async def leaderboard(self, ctx):
        guild_data = self.levels.get(str(ctx.guild.id), {})
        if not guild_data:
            return await ctx.send("No data.")

        top = sorted(
            guild_data.items(),
            key=lambda x: (x[1]["prestige"], x[1]["level"], x[1]["xp"]),
            reverse=True
        )[:10]

        embed = discord.Embed(title="🏆 Leaderboard", color=discord.Color.gold())
        for i, (uid, data) in enumerate(top, 1):
            member = ctx.guild.get_member(int(uid))
            name = member.display_name if member else "Unknown"
            embed.add_field(
                name=f"{i}. {name}",
                value=f"P{data['prestige']} | L{data['level']} | XP {data['xp']}",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command()
    async def rank(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        data = self.get_user(str(ctx.guild.id), str(member.id))

        img = Image.new("RGB", (600, 180), (30, 30, 30))
        draw = ImageDraw.Draw(img)

        font = ImageFont.load_default()

        draw.text((20, 20), member.display_name, font=font, fill=(255, 255, 255))
        draw.text((20, 60), f"Level: {data['level']}", font=font, fill=(255, 255, 255))
        draw.text((20, 90), f"Prestige: {data['prestige']}", font=font, fill=(255, 255, 255))
        draw.text((20, 120), f"XP: {data['xp']}", font=font, fill=(255, 255, 255))

        path = "rank.png"
        img.save(path)
        await ctx.send(file=discord.File(path))


async def setup(bot):
    await bot.add_cog(Leveling(bot))
