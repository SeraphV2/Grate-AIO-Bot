# cogs/music.py
# Requirements (recommended):
#   Python 3.12 (or 3.11)
#   pip install -U discord.py yt-dlp youtube-search-python PyNaCl
#   FFmpeg installed (or set FFMPEG_EXE below)

import os
import asyncio
import discord
from discord.ext import commands
from discord import FFmpegPCMAudio
import yt_dlp
from youtube_search import YoutubeSearch

# ---- CONFIG ----
# If ffmpeg is NOT in PATH, set this to your ffmpeg.exe full path, e.g. r"C:\ffmpeg\bin\ffmpeg.exe"
FFMPEG_EXE = os.getenv("C:\ffmpeg\bin\ffmpeg.exe", "").strip()  # optional env override

YTDLP_OPTS = {
    "format": "bestaudio/best",
    "quiet": True,
    "noplaylist": True,
    # Helps yt-dlp behave more consistently
    "default_search": "ytsearch1",
    "source_address": "0.0.0.0",
}

FFMPEG_OPTS = {
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
    "options": "-vn -loglevel warning",
}


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # ---------- helpers ----------
    async def ensure_voice(self, ctx: commands.Context) -> bool:
        """Ensure the bot is connected to the author's voice channel."""
        if ctx.voice_client and ctx.voice_client.is_connected():
            return True

        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send("❌ You must join a voice channel first.")
            return False

        try:
            await ctx.author.voice.channel.connect(timeout=30, reconnect=True)
            return True
        except asyncio.TimeoutError:
            await ctx.send("❌ Timed out connecting to voice. (Often firewall/UDP/network on servers.)")
            return False
        except Exception as e:
            await ctx.send(f"❌ Failed to connect to voice: `{type(e).__name__}`")
            return False

    def build_audio_source(self, audio_url: str) -> FFmpegPCMAudio:
        """Create an FFmpeg audio source, using explicit ffmpeg path if provided."""
        if FFMPEG_EXE:
            return FFmpegPCMAudio(audio_url, executable=FFMPEG_EXE, **FFMPEG_OPTS)
        return FFmpegPCMAudio(audio_url, **FFMPEG_OPTS)

    # ---------- commands ----------
    @commands.command()
    async def join(self, ctx: commands.Context):
        """Join the author's voice channel."""
        ok = await self.ensure_voice(ctx)
        if ok:
            await ctx.send(f"🎧 Joined **{ctx.voice_client.channel.name}**")

    @commands.command()
    async def leave(self, ctx: commands.Context):
        """Disconnect from voice."""
        if not ctx.voice_client:
            return await ctx.send("❌ I'm not connected.")
        await ctx.voice_client.disconnect()
        await ctx.send("👋 Disconnected.")

    @commands.command()
    async def stop(self, ctx: commands.Context):
        """Stop playback."""
        if ctx.voice_client and ctx.voice_client.is_playing():
            ctx.voice_client.stop()
            return await ctx.send("⏹️ Stopped.")
        await ctx.send("❌ Nothing is playing.")

    @commands.command()
    async def play(self, ctx: commands.Context, *, query: str):
        """Play from a YouTube URL or search query."""
        if not await self.ensure_voice(ctx):
            return

        # Resolve query to URL (ytsearch1 is handled by yt-dlp too, but we keep this for embed/link)
        if query.startswith("http://") or query.startswith("https://"):
            url = query
        else:
            results = YoutubeSearch(query, max_results=1).to_dict()
            if not results:
                return await ctx.send("❌ No results found.")
            url = f"https://www.youtube.com{results[0]['url_suffix']}"

        # Extract stream URL via yt-dlp
        try:
            with yt_dlp.YoutubeDL(YTDLP_OPTS) as ydl:
                info = ydl.extract_info(url, download=False)
                audio_url = info["url"]
        except Exception as e:
            # Common: yt-dlp needs update / JS challenges / no node
            return await ctx.send(
                "❌ Failed to fetch audio.\n"
                f"Error: `{type(e).__name__}`\n"
                "Tip: `pip install -U yt-dlp` and install Node.js LTS if you see YouTube signature warnings."
            )

        # Build ffmpeg source
        try:
            source = self.build_audio_source(audio_url)
        except discord.ClientException as e:
            # This is where you'll see: "ffmpeg was not found."
            msg = str(e)
            if "ffmpeg was not found" in msg.lower():
                return await ctx.send(
                    "❌ FFmpeg was not found.\n"
                    "Install FFmpeg and add it to PATH, or set FFMPEG_EXE to your ffmpeg.exe path."
                )
            return await ctx.send(f"❌ Audio source error: `{type(e).__name__}`")

        # Play
        vc = ctx.voice_client
        if vc.is_playing():
            vc.stop()
        vc.play(source)

        # Embed
        title = info.get("title", "Unknown Title")
        thumb = info.get("thumbnail")
        embed = discord.Embed(
            title="🎶 Now Playing",
            description=f"[{title}]({url})",
            color=discord.Color.blurple(),
        )
        if thumb:
            embed.set_thumbnail(url=thumb)

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
