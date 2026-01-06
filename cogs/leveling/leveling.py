import discord
from discord.ext import commands, tasks
import json
import os
import time
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

from settings import *

LEVELS_FILE = "levels.json"


# ---------------- FILE UTILS ---------------- #

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


# ================================
#            COG
# ================================

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.levels = load_levels()
        self.text_cooldowns = {}
        self.voice_xp.start()

    # ---------------- USER DATA ---------------- #

    def get_user(self, guild_id, user_id):
        self.levels.setdefault(guild_id, {})
        self.levels[guild_id].setdefault(user_id, {
            "xp": 0,
            "level": 0,
            "prestige": 0
        })
        return self.levels[guild_id][user_id]

    # ---------------- ROLES ---------------- #

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

            try:
                await member.send(f"🌟 You prestiged! Prestige **{data['prestige']}**")
            except:
                pass

    # ---------------- MESSAGE XP ---------------- #

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

            channel = self.bot.get_channel(LEVEL_UP_CHANNEL_ID) if LEVEL_UP_CHANNEL_ID else message.channel
            await channel.send(LEVEL_UP_MESSAGE.format(member=message.author.mention, level=data["level"]))

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

                    data = self.get_user(str(guild.id), str(member.id))
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

        embed = discord.Embed(
            title=f"📊 {member.display_name}'s Level",
            color=discord.Color.blurple()
        )
        embed.add_field(name="Level", value=data["level"])
        embed.add_field(name="Prestige", value=data["prestige"])
        embed.add_field(name="XP", value=f"{data['xp']} / {xp_for_next_level(data['level'])}")

        await ctx.send(embed=embed)

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
                value=f"⭐ {data['prestige']} | 🔰 {data['level']} | XP {data['xp']}",
                inline=False
            )

        await ctx.send(embed=embed)

    # ---------------- PREMIUM RANK CARD ---------------- #

    @commands.command()
    async def rank(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        gid = str(ctx.guild.id)
        uid = str(member.id)
        data = self.get_user(gid, uid)

        # Get rank position
        guild_data = self.levels.get(gid, {})
        sorted_users = sorted(
            guild_data.items(),
            key=lambda x: (x[1]["prestige"], x[1]["level"], x[1]["xp"]),
            reverse=True
        )
        rank_pos = next(i + 1 for i, (u, _) in enumerate(sorted_users) if u == uid)

        level = data["level"]
        xp = data["xp"]
        prestige = data["prestige"]
        needed = xp_for_next_level(level)
        percent = xp / needed

        W, H = 900, 280
        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Neon gradient
        for y in range(H):
            r = int(40 + y * 0.4)
            g = int(20 + y * 0.2)
            b = int(80 + y * 0.5)
            draw.line((0, y, W, y), fill=(r, g, b))

        # Glass panel
        panel = Image.new("RGBA", (860, 240), (20, 20, 25, 220))
        img.paste(panel, (20, 20), panel)

        # Fonts
        font_big = ImageFont.truetype("arial.ttf", 38)
        font_med = ImageFont.truetype("arial.ttf", 26)
        font_small = ImageFont.truetype("arial.ttf", 18)

        # Avatar
        avatar_asset = member.display_avatar.with_size(128)
        avatar_bytes = await avatar_asset.read()
        avatar = Image.open(BytesIO(avatar_bytes)).convert("RGBA").resize((120, 120))

        #glow = Image.new("RGBA", (140, 140), (20, 20, 25, 220))
        #img.paste(glow, (50, 70), glow)

        mask = Image.new("L", (120, 120), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, 120, 120), fill=255)
        img.paste(avatar, (60, 80), mask)

        # Text
        draw.text((210, 60), member.display_name, font=font_big, fill="white")
        draw.text((210, 110), f"LEVEL {level}", font=font_med, fill="#00ffff")
        draw.text((210, 145), f"Prestige {prestige}", font=font_small, fill="#ffd700")
        draw.text((210, 170), f"Rank #{rank_pos}", font=font_small, fill="#ff88ff")

        # XP Bar
        bx, by, bw, bh = 210, 215, 620, 26
        draw.rectangle((bx, by, bx + bw, by + bh), fill="#1c1f26")
        draw.rectangle((bx, by, bx + int(bw * percent), by + bh), fill="#00ffe1")
        draw.text((bx, by - 22), f"{xp:,} / {needed:,} XP", font=font_small, fill="white")

        path = f"rank_{member.id}.png"
        img.save(path)
        await ctx.send(file=discord.File(path))


async def setup(bot):
    await bot.add_cog(Leveling(bot))
