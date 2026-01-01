# Settings for the bot.
# Leave any settings blank if you not to use them.
import dotenv


dotenv.load_dotenv()

#---------------------#Logs#---------------------#

LOG_CHANNEL_ID = 1350069823916343365  # Replace with your desired channel ID

#---------------------#General#---------------------#

DISCORD_BOT_TOKEN = "MTQ0NjQ1MzQ3NDUxMzUxODY4Mw.GAqWJr.WwOROxnskmeAu7wEBTBsWU6iQKoFkoDCQS6PIM"  # Discord bot token from environment variable
BOT_STATUS = "Providing Support"  # Status text of the bot
BOT_PREFIX = "."  # Command prefix
BOT_NAME = "Nexonix Bot" # Bot name
BOT_AUTHOR = "Nexonix Bot By Paradym A Member Of The Nexonix Team"  # Bot author
SUPPORT_CATEGORY_ID = 1447890979507146763  # Category where tickets go
SUPPORT_ROLE_ID = 1350069822662119504      # Support team role ID
SUPPORT_PANEL_CHANNEL_ID = 1449468176638148668  # Channel where panel is sent

# ------------------ WELCOME SETTINGS ------------------ #

# The channel ID where welcome messages will be sent
WELCOME_CHANNEL_ID = 123456789012345678  # <-- Replace with your actual channel ID

# Optional: Customize the welcome message
# You can use placeholders: {member} = mention of the new member, {server} = server name
WELCOME_MESSAGE = "Welcome {member} to {server}! 🎉 Feel free to introduce yourself!"

#---------------------#Anti-Nuke#---------------------#

ANTI_NUKE_ENABLED = True

# Multiple owners (THESE USERS ARE IMMUNE)
ANTI_NUKE_OWNERS = [
    960216572478246992,
    976205015834325003
]

# Action thresholds (within TIME_WINDOW seconds)
ANTI_NUKE_LIMITS = {
    "channel_delete": 2,
    "channel_create": 3,
    "role_delete": 2,
    "role_create": 3,
    "guild_update": 2
}

TIME_WINDOW = 10  # seconds

# Auto-punishment
ANTI_NUKE_PUNISHMENT = "timeout"  # "ban" | "kick" | "timeout"
TIMEOUT_MINUTES = 60

# Panic mode
PANIC_ROLE_NAME = "LOCKED"
PANIC_CHANNEL_NAME = "server-locked"

# Backup file
BACKUP_FILE = "server_backup.json"

#---------------------#Verification#---------------------#

VERIFICATION_ENABLED = True

VERIFICATION_CHANNEL_ID = 1449477926385881108  # channel where verify panel is sent
VERIFIED_ROLE_ID = 1350069822662119501          # role given after verification
UNVERIFIED_ROLE_ID = 1449477003282485351        # role given on join

VERIFICATION_MESSAGE_TITLE = "✅ Server Verification"
VERIFICATION_MESSAGE_DESCRIPTION = (
    "Welcome! Please verify yourself to gain access to the server.\n\n"
    "Click the **Verify** button below."
)

#---------------------#Anti-Alt/Raid#---------------------#

ANTI_ALT_ENABLED = True
ANTI_ALT_MIN_ACCOUNT_AGE = 7  # in days, e.g., accounts younger than this are considered alt accounts
ANTI_ALT_ACTION = "kick"      # "kick" or "ban"

ANTI_RAID_ENABLED = True
ANTI_RAID_MAX_JOIN_RATE = 5   # max members joining per X seconds
ANTI_RAID_TIME_FRAME = 10     # timeframe in seconds to check for multiple joins
RAID_ACTION = "kick"           # action to take on detected raid
ADMIN_ROLE_IDS = [123456789012345678]  # roles that bypass anti-raid checks

#---------------------#RSS#---------------------#

RSS_FEEDS = [
    "https://example.com/feed1.xml",
    "https://example.com/feed2.xml"
]
RSS_CHANNEL_ID = 1350069823576477812  # Channel to post feed items
RSS_POLL_INTERVAL = 300  # In seconds (5 minutes)

#---------------------#Leveling System#---------------------#

LEVELING_ENABLED = True

TEXT_XP_PER_MESSAGE = 10
TEXT_XP_COOLDOWN = 60  # seconds

VOICE_XP_PER_MINUTE = 5
VOICE_XP_CHECK_INTERVAL = 60  # seconds

LEVEL_XP_MULTIPLIER = 1.0

LEVEL_UP_MESSAGE = "🎉 {member} reached **Level {level}**!"
LEVEL_UP_CHANNEL_ID = None  # None = same channel

#----------LEVEL ROLES----------#

LEVEL_ROLES = {
    5: 135000000000000000,
    10: 135000000000000001,
    20: 135000000000000002
}

REMOVE_OLD_LEVEL_ROLES = True

#----------PRESTIGE----------#

PRESTIGE_ENABLED = True
PRESTIGE_LEVEL_REQUIREMENT = 50
PRESTIGE_ROLE_ID = 135000000000000003

#----------REACT ROLES----------#

# Toggle reaction roles on/off
REACTION_ROLES_ENABLED = True

# Map of label -> {"id": role_id, "description": desc}
# To add more copy and paste - "VIP": {"id": 345678901234567890, "description": "Access exclusive VIP channels"},
# id = role id - Make sure u have dev options enabled and right click the role and copy id
REACTION_ROLES = {
    "test": {"id": 1350069822662119504, "description": "Get notifications about gaming events"},
    "Artist": {"id": 1350069822662119504, "description": "Join the creative art discussions"},
    "VIP": {"id": 1350069822662119504, "description": "Access exclusive VIP channels"},
}
