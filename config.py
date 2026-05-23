import os
from dotenv import load_dotenv

load_dotenv()

# ── Bot Configuration ─────────────────────────────────────────────────────────
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
BOT_USERNAME: str = os.getenv("BOT_USERNAME", "")   # without @

# ── Admin IDs (comma-separated in env) ───────────────────────────────────────
_raw_admins = os.getenv("ADMIN_IDS", "")
ADMIN_IDS: list[int] = [
    int(x.strip()) for x in _raw_admins.split(",") if x.strip().isdigit()
]

# ── Database ──────────────────────────────────────────────────────────────────
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///bot.db")

# ── Anti-Spam / Rate-Limiting ─────────────────────────────────────────────────
RATE_LIMIT_SECONDS: int = int(os.getenv("RATE_LIMIT_SECONDS", "3"))

# ── Broadcast ─────────────────────────────────────────────────────────────────
BROADCAST_DELAY: float = float(os.getenv("BROADCAST_DELAY", "0.05"))  # sec between sends

# ── Texts ─────────────────────────────────────────────────────────────────────
BOT_NAME: str = os.getenv("BOT_NAME", "MyBot")
WELCOME_TEXT: str = os.getenv(
    "WELCOME_TEXT",
    "👋 Welcome to <b>{bot_name}</b>!\n\nTo use this bot, please join all required channels first.",
)
