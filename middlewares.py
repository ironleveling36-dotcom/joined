"""
Custom middlewares:
  - RateLimitMiddleware  – simple in-memory per-user cooldown
  - RegisterMiddleware   – ensures every user is saved in DB
"""
from __future__ import annotations

import time
from collections import defaultdict
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject, Update

import database
import messages
import config


# ── Rate-Limit ────────────────────────────────────────────────────────────────
class RateLimitMiddleware(BaseMiddleware):
    def __init__(self, seconds: int = config.RATE_LIMIT_SECONDS) -> None:
        self._seconds = seconds
        self._last_call: dict[int, float] = defaultdict(float)

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user:
            now = time.monotonic()
            if now - self._last_call[user.id] < self._seconds:
                if isinstance(event, Message):
                    await event.answer(messages.RATE_LIMITED)
                elif isinstance(event, CallbackQuery):
                    await event.answer(messages.RATE_LIMITED, show_alert=True)
                return
            self._last_call[user.id] = now
        return await handler(event, data)


# ── Auto-register user ────────────────────────────────────────────────────────
class RegisterMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user:
            await database.get_or_create_user(
                user_id=user.id,
                username=user.username,
                full_name=user.full_name,
            )
        return await handler(event, data)
