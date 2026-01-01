import discord
from discord.ext import commands
import json
import os

CUSTOM_COMMANDS_FILE = "custom_commands.json"

# Ensure the JSON file exists
if not os.path.exists(CUSTOM_COMMANDS_FILE):
    with open(CUSTOM_COMMANDS_FILE, "w") as f:
        json.dump({}, f)

class CustomCommands(commands.Cog):
    """Cog for managing and using custom commands."""

    def __init__(self, bot):
        self.bot = bot
        self.load_commands()

    def load_commands(self):
        """Load commands from JSON."""
        with open(CUSTOM_COMMANDS_FILE, "r") as f:
            self.commands = json.load(f)

    def save_commands(self):
        """Save commands to JSON."""
        with open(CUSTOM_COMMANDS_FILE, "w") as f:
            json.dump(self.commands, f, indent=4)

    # ------------------ Admin Commands ------------------ #
    @commands.group(name="cc", invoke_without_command=True)
    async def cc(self, ctx, *, command_name: str):
        """Trigger a custom command manually using .cc"""
        command_name = command_name.lower()
        if command_name in self.commands:
            cmd_data = self.commands[command_name]
            response = self.replace_variables(cmd_data["response"], ctx.author, ctx.guild)
            if cmd_data.get("embed", False):
                embed = discord.Embed(description=response, colour=discord.Colour.blurple())
                await ctx.send(embed=embed)
            else:
                await ctx.send(response)
        else:
            await ctx.send(f"❌ Command `{command_name}` not found.")

    @cc.command(name="add")
    @commands.has_permissions(administrator=True)
    async def cc_add(self, ctx, name: str, *, response: str):
        """Add a custom command. Use --embed at the end for embed response."""
        name = name.lower()
        embed = False
        if response.endswith(" --embed"):
            response = response[:-8].strip()
            embed = True

        self.commands[name] = {
            "response": response,
            "embed": embed
        }
        self.save_commands()
        await ctx.send(f"✅ Custom command `{name}` added successfully.")

    @cc.command(name="remove")
    @commands.has_permissions(administrator=True)
    async def cc_remove(self, ctx, name: str):
        """Remove a custom command."""
        name = name.lower()
        if name in self.commands:
            self.commands.pop(name)
            self.save_commands()
            await ctx.send(f"✅ Custom command `{name}` removed successfully.")
        else:
            await ctx.send(f"❌ Command `{name}` not found.")

    @cc.command(name="list")
    async def cc_list(self, ctx):
        """List all custom commands."""
        if not self.commands:
            await ctx.send("⚠️ No custom commands have been added yet.")
            return

        embed = discord.Embed(title="📜 Custom Commands", colour=discord.Colour.gold())
        for name, data in self.commands.items():
            value = data["response"]
            if data.get("embed"):
                value += " (Embed)"
            embed.add_field(name=name, value=value, inline=False)
        await ctx.send(embed=embed)

    # ------------------ Auto Trigger ------------------ #
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if not message.guild:
            return

        content = message.content.lower()
        if content.startswith("."):
            command_name = content[1:]  # Remove prefix
            if command_name in self.commands:
                cmd_data = self.commands[command_name]
                response = self.replace_variables(cmd_data["response"], message.author, message.guild)
                if cmd_data.get("embed", False):
                    embed = discord.Embed(description=response, colour=discord.Colour.blurple())
                    await message.channel.send(embed=embed)
                else:
                    await message.channel.send(response)

    # ------------------ Helper ------------------ #
    def replace_variables(self, text: str, user: discord.Member, guild: discord.Guild):
        text = text.replace("{user}", str(user))
        text = text.replace("{mention}", user.mention)
        text = text.replace("{server}", guild.name if guild else "DM")
        return text

async def setup(bot):
    await bot.add_cog(CustomCommands(bot))
