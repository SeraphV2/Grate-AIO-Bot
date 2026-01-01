import os
import discord
from discord.ext import commands
import yt_dlp
import asyncio

# ============================================================
#                      FFMPEG SETUP
# ============================================================

WINDOWS_FFMPEG = r"C:\ffmpeg\bin\ffmpeg.exe"

if os.path.exists(WINDOWS_FFMPEG):
    FFMPEG_EXECUTABLE = WINDOWS_FFMPEG
    print("Music: Using Windows FFmpeg")
else:
    FFMPEG_EXECUTABLE = "ffmpeg"
    print("Music: Using System FFmpeg (Linux/macOS)")

FFMPEG_OPTIONS = {
    "executable": FFMPEG_EXECUTABLE,
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn"
}

# ============================================================
#                     YT-DLP SETTINGS
# ============================================================

YDL_OPTIONS = {
    "format": "bestaudio/best",
    "quiet": True,
    "noplaylist": True,
    "default_search": "auto"
}

# ============================================================
#                         MUSIC COG
# ============================================================

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queues = {}  # guild_id -> [(url, title)]

    # ---------------- INTERNAL ---------------- #

    def get_queue(self, guild_id):
        return self.queues.setdefault(guild_id, [])

    async def connect(self, ctx):
        if not ctx.author.voice:
            await ctx.send("❌ You must be in a voice channel.")
            return None

        if ctx.voice_client:
            return ctx.voice_client

        return await ctx.author.voice.channel.connect()

    async def play_next(self, ctx):
        queue = self.get_queue(ctx.guild.id)
        if not queue:
            return

        url, title = queue.pop(0)

        def after_playing(error):
            if error:
                print(error)
            asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop)

        ctx.voice_client.play(
            discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS),
            after=after_playing
        )

        asyncio.run_coroutine_threadsafe(
            ctx.send(f"🎶 Now playing: **{title}**"),
            self.bot.loop
        )

    async def start_playback(self, ctx, search):
        vc = await self.connect(ctx)
        if not vc:
            return

        with yt_dlp.YoutubeDL(YDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(search, download=False)
                if "entries" in info:
                    info = info["entries"][0]

                url = info["url"]
                title = info["title"]
            except Exception:
                await ctx.send("❌ Could not find that video.")
                return

        if vc.is_playing():
            self.get_queue(ctx.guild.id).append((url, title))
            await ctx.send(f"➕ Added to queue: **{title}**")
            return

        vc.play(
            discord.FFmpegPCMAudio(url, **FFMPEG_OPTIONS),
            after=lambda e: asyncio.run_coroutine_threadsafe(self.play_next(ctx), self.bot.loop)
        )

        await ctx.send(f"🎶 Now playing: **{title}**")

    # ============================================================
    #                         COMMANDS
    # ============================================================

    @commands.command()
    async def join(self, ctx):
        vc = await self.connect(ctx)
        if vc:
            await ctx.send("🔊 Joined voice channel.")

    @commands.command()
    async def leave(self, ctx):
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            self.queues.pop(ctx.guild.id, None)
            await ctx.send("👋 Left the voice channel.")
        else:
            await ctx.send("❌ I'm not in a voice channel.")

    @commands.command()
    async def play(self, ctx, *, search: str):
        """Play YouTube audio from URL or search"""
        await self.start_playback(ctx, search)

    @commands.command()
    async def pause(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.pause()
            await ctx.send("⏸️ Paused.")

    @commands.command()
    async def resume(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_paused():
            ctx.voice_client.resume()
            await ctx.send("▶️ Resumed.")

    @commands.command()
    async def stop(self, ctx):
        if ctx.voice_client:
            ctx.voice_client.stop()
            self.queues[ctx.guild.id] = []
            await ctx.send("⏹️ Stopped.")

    @commands.command()
    async def skip(self, ctx):
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            await ctx.send("⏭️ Skipped.")

    @commands.command()
    async def queue(self, ctx):
        queue = self.get_queue(ctx.guild.id)
        if not queue:
            await ctx.send("📭 Queue is empty.")
            return

        msg = "\n".join(f"{i+1}. {title}" for i, (_, title) in enumerate(queue))
        await ctx.send(f"🎶 **Queue:**\n{msg}")

# ============================================================
#                        SETUP
# ============================================================

async def setup(bot):
    await bot.add_cog(Music(bot))
