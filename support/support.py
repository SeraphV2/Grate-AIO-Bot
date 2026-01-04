import discord
from discord.ext import commands, tasks
import json
import os
from datetime import datetime, timedelta
import settings

TICKET_DB = "tickets.json"
STAFF_DB = "staff_stats.json"

def load(path):
    if not os.path.exists(path):
        return {}
    with open(path,"r") as f:
        return json.load(f)

def save(path,data):
    with open(path,"w") as f:
        json.dump(data,f,indent=4)

class TicketSystem(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        self.tickets = load(TICKET_DB)
        self.staff = load(STAFF_DB)
        self.inactivity_task.start()

    def cog_unload(self):
        self.inactivity_task.cancel()

    def user_open_tickets(self,uid):
        return [t for t in self.tickets.values() if t["user"]==uid and t["open"]]

    def log_staff(self,uid):
        if not settings.TRACK_STAFF_STATS:
            return
        self.staff[str(uid)] = self.staff.get(str(uid),0)+1
        save(STAFF_DB,self.staff)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ticketsetup(self,ctx):
        for cat in set(settings.TICKET_TYPES.values()):
            if not discord.utils.get(ctx.guild.categories,name=cat):
                await ctx.guild.create_category(cat)

        if not discord.utils.get(ctx.guild.text_channels,name=settings.LOG_CHANNEL):
            await ctx.guild.create_text_channel(settings.LOG_CHANNEL)

        embed = discord.Embed(
            title="🎫 Grate-AIO Support Center",
            description=(
                "Open a ticket by selecting a category below.\n\n"
                "🟢 **Support** — Get help\n"
                "🔴 **Report** — Report a user\n"
                "🟡 **Appeal** — Appeal a punishment"
            ),
            color=discord.Color.blurple()
        )
        embed.set_footer(text="Grate-AIO Ticket System")

        await ctx.send(embed=embed, view=TicketPanel())
        await ctx.send("✅ Ticket system ready.")

    @tasks.loop(minutes=5)
    async def inactivity_task(self):
        now = datetime.utcnow()
        for cid,data in list(self.tickets.items()):
            if not data["open"]:
                continue

            channel = self.bot.get_channel(int(cid))
            if not channel:
                continue

            last = channel.last_message.created_at if channel.last_message else datetime.utcnow()
            minutes = (now - last).total_seconds() / 60

            if minutes >= settings.INACTIVITY_CLOSE:
                await channel.send("⏱ Ticket closed due to inactivity.")
                await self.close_ticket(channel)

            elif minutes >= settings.INACTIVITY_WARNING:
                await channel.send("⚠ This ticket will close soon due to inactivity.")

    async def close_ticket(self,channel):
        cid = str(channel.id)
        self.tickets[cid]["open"] = False
        save(TICKET_DB,self.tickets)

        transcript = ""
        async for msg in channel.history(limit=None,oldest_first=True):
            transcript += f"<p><b>{msg.author}</b>: {msg.content}</p>\n"

        html = f"<html><body>{transcript}</body></html>"
        filename = f"ticket-{channel.id}.html"
        with open(filename,"w",encoding="utf8") as f:
            f.write(html)

        log = discord.utils.get(channel.guild.text_channels,name=settings.LOG_CHANNEL)
        if log:
            await log.send(file=discord.File(filename))

        await channel.delete()

class TicketPanel(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketButton("Support","🟢",discord.ButtonStyle.green))
        self.add_item(TicketButton("Report","🔴",discord.ButtonStyle.danger))
        self.add_item(TicketButton("Appeal","🟡",discord.ButtonStyle.secondary))

class TicketButton(discord.ui.Button):
    def __init__(self,ticket_type,emoji,style):
        super().__init__(label=ticket_type, emoji=emoji, style=style)
        self.ticket_type = ticket_type

    async def callback(self,interaction):
        await interaction.response.send_modal(TicketModal(self.ticket_type))

class TicketModal(discord.ui.Modal):
    def __init__(self,ticket_type):
        super().__init__(title=f"{ticket_type} Ticket")
        self.ticket_type = ticket_type
        self.reason = discord.ui.TextInput(label="Describe your issue",style=discord.TextStyle.paragraph)
        self.priority = discord.ui.TextInput(label="Priority (Low, Medium, High)")
        self.add_item(self.reason)
        self.add_item(self.priority)

    async def on_submit(self,interaction):
        guild = interaction.guild
        user = interaction.user
        cog = interaction.client.get_cog("TicketSystem")

        if len(cog.user_open_tickets(user.id)) >= settings.MAX_OPEN_TICKETS:
            return await interaction.response.send_message("❌ Too many open tickets.",ephemeral=True)

        category = discord.utils.get(guild.categories,name=settings.TICKET_TYPES[self.ticket_type])
        staff = discord.utils.get(guild.roles,name=settings.STAFF_ROLE)

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            user: discord.PermissionOverwrite(view_channel=True),
            staff: discord.PermissionOverwrite(view_channel=True)
        }

        emoji = settings.PRIORITIES.get(self.priority.value,"🟢")
        channel = await guild.create_text_channel(
            f"{emoji}-{self.ticket_type}-{user.name}",
            category=category,
            overwrites=overwrites
        )

        cog.tickets[str(channel.id)] = {
            "user": user.id,
            "type": self.ticket_type,
            "priority": self.priority.value,
            "open": True,
            "created": str(datetime.utcnow())
        }
        save(TICKET_DB,cog.tickets)

        ping = ""
        role_name = settings.PRIORITY_PINGS.get(self.priority.value)
        if role_name:
            role = discord.utils.get(guild.roles,name=role_name)
            if role:
                ping = role.mention

        embed = discord.Embed(
            title=f"{emoji} {self.ticket_type} Ticket",
            description=self.reason.value,
            color=discord.Color.orange()
        )
        embed.add_field(name="User", value=user.mention)
        embed.add_field(name="Priority", value=self.priority.value)

        await channel.send(ping, embed=embed)
        await channel.send(settings.AUTO_MESSAGES[self.ticket_type])
        await channel.send("A staff member will assist you shortly.", view=TicketControls())

        await interaction.response.send_message(f"✅ Ticket created: {channel.mention}",ephemeral=True)

class TicketControls(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Claim", style=discord.ButtonStyle.primary)
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        cog = interaction.client.get_cog("TicketSystem")
        cog.log_staff(interaction.user.id)

        # Respond to interaction
        await interaction.response.send_message(
            f"🧑‍💼 {interaction.user.mention} claimed this ticket.",
            ephemeral=True  # optional: only the claimer sees it
        )

        # Optional: notify channel for everyone
        await interaction.channel.send(f"🧑‍💼 {interaction.user.mention} has claimed this ticket.")


    @discord.ui.button(label="Close",style=discord.ButtonStyle.danger)
    async def close(self,interaction,button):
        cog = interaction.client.get_cog("TicketSystem")
        await cog.close_ticket(interaction.channel)

async def setup(bot):
    await bot.add_cog(TicketSystem(bot))
