"""
Centralised message texts (HTML parse mode).
"""

WELCOME = (
    "👋 <b>Welcome to {bot_name}!</b>\n\n"
    "To access this bot's features, you must join all required channels.\n\n"
    "👇 Click the buttons below to join, then press <b>Verify</b>."
)

NOT_JOINED = (
    "❌ <b>Access Denied</b>\n\n"
    "You haven't joined all required channels yet.\n\n"
    "👇 Steps to fix:\n"
    "1. Click each channel button below\n"
    "2. Press <b>Join</b> inside the channel\n"
    "3. Come back and press ✅ <b>Verify</b>"
)

ALREADY_VERIFIED = (
    "✅ <b>You're already verified!</b>\n\n"
    "Enjoy using the bot."
)

VERIFIED_SUCCESS = (
    "🎉 <b>Verification Successful!</b>\n\n"
    "You're now a verified member. Welcome aboard!"
)

# ── Default welcome message (shown after verification) ────────────────────────
# Admin can override this from the admin panel.
# Supports placeholders: {first_name}, {last_name}, {username}, {user_id}
DEFAULT_WELCOME_MESSAGE = (
    "🎊 <b>Welcome, {first_name}!</b>\n\n"
    "You have successfully joined and verified.\n\n"
    "✅ You now have full access to the bot.\n"
    "Enjoy your stay! 🚀"
)

WELCOME_MSG_SETTING_KEY = "welcome_message"

NO_CHANNELS = (
    "ℹ️ No force-join channels are configured yet.\n"
    "The bot is open to everyone."
)

HOME = (
    "🏠 <b>Home</b>\n\n"
    "You're verified and good to go! Use the menu below."
)

ABOUT = (
    "ℹ️ <b>About</b>\n\n"
    "This bot is powered by a professional force-join system.\n"
    "Built with ❤️ using Python + aiogram 3."
)

SUPPORT = (
    "📞 <b>Support</b>\n\n"
    "Need help? Contact the admin."
)

ADMIN_WELCOME = (
    "🛡 <b>Admin Panel</b>\n\n"
    "Welcome, {name}! Select an option below."
)

BROADCAST_CHOOSE_TYPE = (
    "📢 <b>Broadcast</b>\n\n"
    "Choose the type of message you want to send to all verified users."
)

BROADCAST_SEND_TEXT = (
    "✉️ <b>Text Broadcast</b>\n\n"
    "Send the message you want to broadcast.\n"
    "<i>HTML formatting is supported.</i>"
)

BROADCAST_PREVIEW = (
    "👁 <b>Preview your broadcast</b>\n\n"
    "{preview}\n\n"
    "Ready to send to <b>{count}</b> verified users?"
)

BROADCAST_DONE = (
    "✅ <b>Broadcast Complete</b>\n\n"
    "📤 Sent:   <b>{sent}</b>\n"
    "❌ Failed: <b>{failed}</b>"
)

ADD_CHANNEL_INSTRUCTIONS = (
    "➕ <b>Add Force-Join Channel</b>\n\n"
    "Send me the channel details in this format:\n\n"
    "<code>CHANNEL_ID | https://t.me/channel | Channel Name</code>\n\n"
    "Example:\n"
    "<code>@mychannel | https://t.me/mychannel | My Channel</code>\n\n"
    "<i>Make sure the bot is an admin in the channel.</i>"
)

REMOVE_CHANNEL_INSTRUCTIONS = (
    "➖ <b>Remove Force-Join Channel</b>\n\n"
    "Send the <b>Channel ID</b> to remove.\n\n"
    "Example: <code>-1001234567890</code> or <code>@mychannel</code>"
)

BLOCK_USER_INSTRUCTIONS = (
    "🚫 <b>Block User</b>\n\n"
    "Send the <b>User ID</b> to block.\n\n"
    "Example: <code>123456789</code>"
)

STATS_TEMPLATE = (
    "📊 <b>Bot Statistics</b>\n\n"
    "👥 Total Users:    <b>{total}</b>\n"
    "✅ Verified Users: <b>{verified}</b>\n"
    "📢 Force Channels: <b>{channels}</b>"
)

# ── Welcome message admin strings ─────────────────────────────────────────────
WELCOME_MSG_PANEL = (
    "✏️ <b>Edit Welcome Message</b>\n\n"
    "<b>Current message:</b>\n"
    "┌─────────────────\n"
    "{current}\n"
    "└─────────────────\n\n"
    "<b>Available placeholders:</b>\n"
    "• <code>{first_name}</code> – user's first name\n"
    "• <code>{last_name}</code>  – user's last name\n"
    "• <code>{username}</code>   – @username (or 'N/A')\n"
    "• <code>{user_id}</code>    – Telegram user ID\n\n"
    "<i>HTML tags like &lt;b&gt;, &lt;i&gt;, &lt;code&gt; are supported.</i>"
)

WELCOME_MSG_INSTRUCTIONS = (
    "✏️ <b>Edit Welcome Message</b>\n\n"
    "Send your new welcome message now.\n\n"
    "<b>Available placeholders:</b>\n"
    "• <code>{first_name}</code> – user's first name\n"
    "• <code>{last_name}</code>  – user's last name\n"
    "• <code>{username}</code>   – @username (or 'N/A')\n"
    "• <code>{user_id}</code>    – Telegram user ID\n\n"
    "Example:\n"
    "<code>🎉 Welcome, {first_name}! You're now verified.</code>"
)

WELCOME_MSG_PREVIEW = (
    "👁 <b>Preview Welcome Message</b>\n\n"
    "This is how it will look to a user:\n\n"
    "┌─────────────────\n"
    "{preview}\n"
    "└─────────────────\n\n"
    "Save this as the new welcome message?"
)

WELCOME_MSG_SAVED = (
    "✅ <b>Welcome message updated!</b>\n\n"
    "New verified users will see the updated message."
)

WELCOME_MSG_RESET = (
    "🔄 <b>Welcome message reset to default.</b>"
)

NOT_ADMIN = "⛔ You don't have permission to use this command."
RATE_LIMITED = "⏳ You're sending requests too fast. Please wait a moment."
ERROR_GENERIC = "⚠️ Something went wrong. Please try again later."
