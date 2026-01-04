import discord
from discord.ext import commands, tasks
import feedparser
from datetime import datetime
from settings import RSS_FEEDS, RSS_CHANNEL_ID, RSS_POLL_INTERVAL  # Define in settings

class RSSMonitor(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.seen_entries = {}  # Keep track of posted entries
        for feed_url in RSS_FEEDS:
            self.seen_entries[feed_url] = set()
        self.check_feeds.start()  # Start the background task

    def cog_unload(self):
        self.check_feeds.cancel()  # Stop the task when cog is unloaded

    @tasks.loop(seconds=RSS_POLL_INTERVAL)
    async def check_feeds(self):
        channel = self.bot.get_channel(RSS_CHANNEL_ID)
        if not channel:
            return

        for feed_url in RSS_FEEDS:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:5]:  # Only check latest 5 posts
                entry_id = entry.get("id") or entry.get("link")
                if entry_id in self.seen_entries[feed_url]:
                    continue  # Already posted
                # Mark as seen
                self.seen_entries[feed_url].add(entry_id)

                # Create embed for the feed item
                embed = discord.Embed(
                    title=entry.get("title", "No title"),
                    url=entry.get("link", ""),
                    description=entry.get("summary", "No description"),
                    color=discord.Color.blue(),
                    timestamp=datetime.utcnow()
                )
                embed.set_author(name=feed.feed.get("title", "RSS Feed"))
                await channel.send(embed=embed)

    @check_feeds.before_loop
    async def before_check(self):
        await self.bot.wait_until_ready()  # Wait until bot is ready

    # Optional admin command to manually check feeds
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def rsscheck(self, ctx):
        """Manually trigger RSS feed check."""
        await ctx.send("Checking RSS feeds...")
        await self.check_feeds()

async def setup(bot: commands.Bot):
    await bot.add_cog(RSSMonitor(bot))
