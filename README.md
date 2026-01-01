# Grate-AIO-Bot
[![Ask DeepWiki](https://devin.ai/assets/askdeepwiki.png)](https://deepwiki.com/SeraphV2/Grate-AIO-Bot)

Grate-AIO-Bot is a comprehensive, all-in-one Discord bot built with Python and discord.py. It offers a wide array of features ranging from robust server security and moderation to member engagement and utility commands.

## Features

-   **Advanced Security Suite:**
    -   **Anti-Nuke:** Protects your server from unauthorized mass deletions of channels and roles. Includes a server backup and restore functionality.
    -   **Anti-Alt:** Automatically moderates newly created accounts to prevent malicious users from joining.
    -   **Anti-Raid:** Detects and takes action against rapid join-raids.
-   **Administration & Moderation:**
    -   A full suite of moderation tools including `ban`, `kick`, `purge`, `lock`, `unlock`, and `slowmode`.
    -   A persistent warning system (`warn`, `warnings`, `clearwarns`) with automated actions after a certain number of infractions.
-   **Member Management:**
    -   **Verification System:** A button-based verification panel to grant roles to new members, keeping your community secure.
    -   **Welcome System:** Automatically greets new members in a designated channel.
-   **Support Ticket System:**
    -   A professional ticket system using modals and persistent buttons, allowing users to easily open support requests in dedicated channels.
-   **Comprehensive Logging:**
    -   Logs a wide variety of server events to a specified channel, including command usage, message edits/deletes, member joins/leaves, role/channel changes, and bans/unbans.
-   **Fun and Utility Commands:**
    -   Engage your community with commands like `eightball`, `coinflip`, `dice`, `rate`, `joke`, `howgay`, and `smashorpass`.
    -   Get random animal pictures with `cat` and `dog`.
-   **RSS Feed Monitoring:**
    -   Automatically posts updates from your favorite RSS feeds directly into a Discord channel.
-   **Remote Server Management:**
    -   Allows whitelisted administrators to execute powerful commands (like announcements or a server nuke) on any server the bot is in, all from a central control server.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/SeraphV2/Grate-AIO-Bot.git
    cd Grate-AIO-Bot
    ```

2.  **Install dependencies:**
    It is recommended to use a virtual environment.
    ```bash
    pip install -r requirements.txt
    ```

3.  **Create an environment file:**
    Create a file named `.env` in the root directory of the project and add your bot's token:
    ```env
    DISCORD_BOT_TOKEN="YOUR_BOT_TOKEN_HERE"
    ```

4.  **Configure the Bot:**
    Open `settings.py` and modify the placeholders to match your server's needs. This includes channel IDs, role IDs, and other behavior toggles. See the [Configuration](#configuration) section for more details.

5.  **Run the bot:**
    ```bash
    python bot.py
    ```

## Configuration

All core settings are located in `settings.py`. These values are used as defaults when the bot joins a new server or when specific systems are initialized.

### Core Settings
-   `DISCORD_BOT_TOKEN`: The bot's token (loaded from `.env`).
-   `BOT_PREFIX`: The command prefix for the bot (e.g., `.`).
-   `BOT_STATUS`: The status message displayed under the bot's name.

### Main System IDs
You **must** replace the placeholder IDs in the various cog files and `settings.py` for the bot to function correctly. Key settings to configure include:

-   `settings.py`:
    -   `welcome_channel_id`
    -   `verification_channel_id`, `verified_role_id`, `unverified_role_id`
    -   `support_category_id`, `support_role_id`, `support_panel_channel_id`
    -   `rss_channel_id`
-   `cogs/logs/logs.py`:
    -   `LOG_CHANNEL_ID`
-   `cogs/remote/remote.py`:
    -   `ALLOWED_IDS`: A set of user IDs who can use remote commands.
    -   `CONTROL_SERVER_ID`: The ID of the server from which remote commands can be executed.

### System Toggles
You can enable or disable entire systems globally within `settings.py`:
-   `welcome_enabled`
-   `verification_enabled`
-   `support_enabled`
-   `anti_nuke_enabled`
-   `anti_alt_enabled`
-   `anti_raid_enabled`

## Usage & Commands

The bot uses `.` as its default prefix. Here is an overview of the main commands.

### Admin & Moderation (`.admin`)
-   `.admin`: Displays an interactive control panel for administrators.
-   `.ban <@member> [reason]`: Bans a user.
-   `.kick <@member> [reason]`: Kicks a user.
-   `.warn <@member> [reason]`: Warns a user.
-   `.warnings <@member>`: Lists all warnings for a user.
-   `.clearwarns <@member>`: Clears all warnings for a user.
-   `.purge [amount]`: Deletes a specified number of messages.
-   `.lock` / `.unlock`: Locks or unlocks the current channel.
-   `.slowmode <seconds>`: Sets a slowmode delay for the channel.

### Security
-   `.antinuke`: Shows the status of the anti-nuke system.
-   `.backup`: Creates a backup of the server's roles and channels.
-   `.panic`: Activates an emergency lockdown of the server.
-   `.antiraid enable/disable <alt|raid>`: Toggles the anti-alt or anti-raid systems.

### Support
-   `.supportpanel`: Sends the ticket creation panel to the configured channel.
-   `.close`: Closes the current support ticket (can only be used in a ticket channel by staff).

### Member Systems
-   `.verifypanel`: Sends the verification panel to the configured channel.
-   `.help`: Displays an interactive panel for fun commands.
-   `.info`: Shows information about the bot.

### Fun (`.fun`)
-   `.fun`: Shows a list of all fun commands.
-   `.eightball <question>`: Ask the magic 8-ball.
-   `.coinflip`: Flips a coin.
-   `.dice [sides]`: Rolls a dice.
-   `.rate <thing>`: Rates something out of 100.
-   `.joke`: Tells a random joke.
-   `.cat` / `.dog`: Sends a random picture of a cat or dog.
-   `.howgay [@user]`: Rates how gay you or another user is.

### Remote Administration
-   `.servers`: Lists all servers the bot is in (owner only).
-   `.remote <server_id> <command> [args]`: Executes a command on a remote server.
    -   _Example_: `.remote 123456789 announce #general Hello from the control server!`
