import discord
from discord.ext import commands
import logging

from settings import (
    VERIFICATION_ENABLED,
    VERIFICATION_CHANNEL_ID,
    VERIFIED_ROLE_ID,
    UNVERIFIED_ROLE_ID,
    VERIFICATION_MESSAGE_TITLE,
    VERIFICATION_MESSAGE_DESCRIPTION
)

logger = logging.getLogger(__name__)

# ---------------------------
# Verify Button View
class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)  # persistent view

    @discord.ui.button(
        label="Verify",
        style=discord.ButtonStyle.green,
        custom_id="verify_button"
    )
    async def verify(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user

        verified_role = guild.get_role(VERIFIED_ROLE_ID)
        unverified_role = guild.get_role(UNVERIFIED_ROLE_ID)

        if not verified_role or not unverified_role:
            return await interaction.response.send_message(
                "❌ Verification roles are misconfigured.",
                ephemeral=True
            )

        if verified_role in member.roles:
            return await interaction.response.send_message(
                "✅ You are already verified.",
                ephemeral=True
            )

        try:
            await member.remove_roles(unverified_role)
            await member.add_roles(verified_role)
            await interaction.response.send_message(
                "🎉 You have been verified! Welcome!",
                ephemeral=True
            )
        except discord.Forbidden:
            await interaction.response.send_message(
                "❌ I don’t have permission to manage roles.",
                ephemeral=True
            )


# ---------------------------
# Verification Cog
class Verification(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        bot.add_view(VerifyView())  # persistent
        logger.info("Verification cog loaded")

    # ---------------------------
    # Auto role on join
    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if not VERIFICATION_ENABLED:
            return

        role = member.guild.get_role(UNVERIFIED_ROLE_ID)
        if role:
            try:
                await member.add_roles(role, reason="New member verification")
            except:
                pass

    # ---------------------------
    # Send verification panel
    @commands.command(name="verifypanel")
    @commands.has_permissions(administrator=True)
    @commands.guild_only()
    async def verify_panel(self, ctx: commands.Context):
        channel = ctx.guild.get_channel(VERIFICATION_CHANNEL_ID)
        if not channel:
            return await ctx.send("❌ Verification channel not found.")

        embed = discord.Embed(
            title=VERIFICATION_MESSAGE_TITLE,
            description=VERIFICATION_MESSAGE_DESCRIPTION,
            color=discord.Color.green()
        )

        await channel.send(embed=embed, view=VerifyView())
        await ctx.send("✅ Verification panel sent.")

async def setup(bot: commands.Bot):
    await bot.add_cog(Verification(bot))
