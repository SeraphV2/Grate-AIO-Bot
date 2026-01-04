import discord
from discord.ext import commands
import settings  # Your settings.py file

class ReactionRoles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.enabled = settings.REACTION_ROLES_ENABLED
        self.roles = settings.REACTION_ROLES  # Dict of {label: {"id": role_id, "description": desc}}

        if self.enabled:
            # Add the persistent view
            bot.add_view(RoleSelectView(self.roles))


    @commands.command(name="reactionroles")
    @commands.has_permissions(administrator=True)
    async def reactionroles(self, ctx: commands.Context):
        """Send the reaction roles embed with dropdown"""
        if not self.enabled:
            return await ctx.send("❌ Reaction roles are currently disabled in settings.")

        embed = discord.Embed(
            title="🎭 Choose Your Role",
            description="Select a role from the dropdown menu below.",
            color=discord.Color.blurple()
        )
        await ctx.send(embed=embed, view=RoleSelectView(self.roles))


# Persistent View
class RoleSelectView(discord.ui.View):
    def __init__(self, roles: dict):
        super().__init__(timeout=None)  # Persistent view must have no timeout
        self.roles = roles
        self.add_item(RoleSelect(roles))


class RoleSelect(discord.ui.Select):
    def __init__(self, roles: dict):
        options = [
            discord.SelectOption(
                label=label,
                description=roles[label]["description"][:100]  # Max 100 chars
            )
            for label in roles
        ]
        super().__init__(
            placeholder="Select your role...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="reaction_roles_select"
        )

    async def callback(self, interaction: discord.Interaction):
        role_id = self.view.roles[self.values[0]]["id"]  # <-- FIXED HERE
        role = interaction.guild.get_role(role_id)
        if not role:
            return await interaction.response.send_message("❌ Role not found.", ephemeral=True)

        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(f"✅ Removed role `{role.name}`", ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(f"✅ Assigned role `{role.name}`", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(ReactionRoles(bot))
