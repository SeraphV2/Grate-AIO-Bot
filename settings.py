# settings.py
# GLOBAL bot-wide configuration ONLY
# All per-guild config lives in the database

import os
import dotenv

dotenv.load_dotenv()

# ==================================================
# BOT CORE (GLOBAL – NEVER PER GUILD)
# ==================================================

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN") or "PUT_TOKEN_IN_ENV"
BOT_NAME = "" # Name of the bot
BOT_AUTHOR = "" # Feel special and add our own name
BOT_STATUS = "" # This is the rich presence of the bot - Basically the bots bio

# Fallback prefix ONLY (used for DMs or DB failure)
BOT_PREFIX = "."

# ==================================================
# DATABASE
# ==================================================

DATABASE_PATH = "database/bot.db"

# ==================================================
# LOGGING
# ==================================================

LOG_LEVEL = "INFO"

# ==================================================
# DEFAULT GUILD SETTINGS
# ⚠️ IMPORTANT:
# These are ONLY used when the bot joins a server
# They are copied INTO THE DATABASE
# After that, the database is the source of truth
# ==================================================

DEFAULT_GUILD_SETTINGS = {

    # --------------------------
    # Command System
    # --------------------------
    "command_prefix": ".",


    # --------------------------
    # Welcome System
    # --------------------------
    "welcome_enabled": True,
    "welcome_channel_id": None,
    "welcome_message": "👋 Welcome {user} to **{server}**!",


    # --------------------------
    # Verification System
    # --------------------------
    "verification_enabled": True,
    "verification_channel_id": None,
    "verified_role_id": None,
    "unverified_role_id": None,
    "verification_message": "✅ Click the button below to verify and gain access to the server.",


    # --------------------------
    # Support / Tickets
    # --------------------------
    "support_enabled": True,
    "support_category_id": None,
    "support_role_id": None,
    "support_panel_channel_id": None,
    "support_open_message": "🎫 Need help? Click the button below to open a support ticket.",
    "support_created_message": "✅ Your support ticket has been created. A team member will assist you shortly.",


    # --------------------------
    # Anti-Nuke System
    # --------------------------
    "anti_nuke_enabled": True,
    "anti_nuke_punishment": "timeout",   # timeout | kick | ban
    "anti_nuke_timeout_minutes": 60,


    # --------------------------
    # Anti-Alt System
    # --------------------------
    "anti_alt_enabled": True,
    "anti_alt_min_account_age": 7,        # days
    "anti_alt_action": "kick",             # kick | ban


    # --------------------------
    # Anti-Raid System
    # --------------------------
    "anti_raid_enabled": True,
    "anti_raid_max_join_rate": 5,          # joins
    "anti_raid_time_frame": 10,             # seconds
    "anti_raid_action": "kick",


    # --------------------------
    # RSS System
    # --------------------------
    "rss_enabled": False,
    "rss_channel_id": None,
    "rss_poll_interval": 300                # seconds
}
