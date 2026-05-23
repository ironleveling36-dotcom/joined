"""
Entry point – polling mode (works on Railway, VPS, local).
"""
from __future__ import annotations

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

import config
import database
from handlers import admin, user
from middlewares import RateLimitMiddleware, RegisterMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


async def main() -> None:
    if not config.BOT_TOKEN:
        logger.error("BOT_TOKEN is not set. Check your .env file.")
        sys.exit(1)

    # ── DB init ────────────────────────────────────────────────────────────────
    await database.init_db()
    logger.info("Database initialised.")

    # ── Bot & Dispatcher ───────────────────────────────────────────────────────
    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # ── Middlewares (order matters) ────────────────────────────────────────────
    dp.message.middleware(RegisterMiddleware())
    dp.callback_query.middleware(RegisterMiddleware())
    dp.message.middleware(RateLimitMiddleware())
    dp.callback_query.middleware(RateLimitMiddleware())

    # ── Routers ────────────────────────────────────────────────────────────────
    dp.include_router(admin.router)   # admin first (more specific filters)
    dp.include_router(user.router)

    # ── Start polling ──────────────────────────────────────────────────────────
    me = await bot.get_me()
    logger.info(f"Starting bot @{me.username} (id={me.id})")

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        logger.info("Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())
