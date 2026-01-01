import discord
from discord.ext import commands
import logging
import settings

logger = logging.getLogger(__name__)


# -----------------------------
# Modal
# -----------------------------
class TicketModal(discord.ui.Modal):
    def __init__(self):
        super().__init__(title="Support Ticket")

        self.issue = discord.ui.TextInput(
            label="Describe your issue",
            style=discord.TextStyle.paragraph,
            placeholder="Explain your problem here...",
            required=True,
            max_length=1000
        )

        self.add_item(self.issue)

    async def on_submit(self, interaction: discord.Interaction):
        guild = interaction.guild
        user = interaction.user

        category = guild.get_channel(settings.SUPPORT_CATEGORY_ID)
        if not category:
            return await interaction.response.send_message(
                "❌ Support category is not configured.",
                ephemeral=True
            )

        # Prevent duplicate tickets
        for channel in category.text_channels:
            if channel.topic == str(user.id):
                return await interaction.response.send_message(
                    "❌ You already have an open ticket.",
                    ephemeral=True
                )

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, manage_channels=True),
        }

        support_role = guild.get_role(settings.SUPPORT_ROLE_ID)
        if support_role:
            overwrites[support_role] = discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True
            )

        channel = await guild.create_text_channel(
            name=f"ticket-{user.id}",
            category=category,
            topic=str(user.id),
            overwrites=overwrites,
            reason="New support ticket"
        )

        embed = discord.Embed(
            title="🎫 New Support Ticket",
            color=discord.Color.green()
        )
        embed.add_field(name="User", value=user.mention, inline=False)
        embed.add_field(name="Issue", value=self.issue.value, inline=False)

        await channel.send(embed=embed)

        await interaction.response.send_message(
            f"✅ Your ticket has been created: {channel.mention}",
            ephemeral=True
        )


# -----------------------------
# Persistent View (CORRECT)
# -----------------------------
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Open Ticket",
        style=discord.ButtonStyle.green,
        emoji="🎫",
        custom_id="support_open_ticket"
    )
    async def open_ticket(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await interaction.response.send_modal(TicketModal())


# -----------------------------
# Cog
# -----------------------------
class Support(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        # Register persistent view ONCE on startup
        bot.add_view(TicketView())

        logger.info("Support cog initialized")

    @commands.command(name="supportpanel")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def support_panel(self, ctx: commands.Context):
        if ctx.channel.id != settings.SUPPORT_PANEL_CHANNEL_ID:
            return await ctx.send(
                "❌ This command can only be used in the support panel channel."
            )

        embed = discord.Embed(
            title="🎫 Support Tickets",
            description="Click the button below to open a support ticket.",
            color=discord.Color.blue()
        )

        await ctx.send(embed=embed, view=TicketView())

    @commands.command(name="close")
    @commands.guild_only()
    async def close_ticket(self, ctx: commands.Context):
        channel = ctx.channel

        if not channel.category or channel.category.id != settings.SUPPORT_CATEGORY_ID:
            return await ctx.send("❌ This is not a support ticket channel.")

        support_role = ctx.guild.get_role(settings.SUPPORT_ROLE_ID)

        if not (
            ctx.author.guild_permissions.administrator
            or (support_role and support_role in ctx.author.roles)
        ):
            return await ctx.send("❌ You do not have permission to close this ticket.")

        await ctx.send("🔒 Closing ticket in **5 seconds**...")
        await discord.utils.sleep_until(
            discord.utils.utcnow() + discord.timedelta(seconds=5)
        )
        await channel.delete(reason="Support ticket closed")


async def setup(bot: commands.Bot):
    await bot.add_cog(Support(bot))
