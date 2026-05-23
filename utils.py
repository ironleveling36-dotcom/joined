"""
Utility helpers.
"""
from __future__ import annotations

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

from database import ForceChannel, get_force_channels
import config


async def check_membership(bot: Bot, user_id: int) -> tuple[bool, list[ForceChannel]]:
    """
    Returns (all_joined: bool, not_joined_channels: list[ForceChannel]).
    If there are no force channels configured, returns (True, []).

    ChatMemberStatus values that mean NOT a member:
      left      – user left on their own
      kicked    – user was banned
      restricted – user is restricted (may or may not be able to read)
    We intentionally do NOT block on "restricted" alone — Telegram considers
    restricted users as still being in the chat. Only "left" and "kicked"
    mean the user hasn't joined.
    """
    channels = await get_force_channels()
    if not channels:
        return True, []

    not_joined: list[ForceChannel] = []
    for ch in channels:
        try:
            member = await bot.get_chat_member(chat_id=ch.channel_id, user_id=user_id)
            # FIX: "restricted" users ARE members — removed it from the block list
            if member.status in ("left", "kicked"):
                not_joined.append(ch)
        except (TelegramBadRequest, TelegramForbiddenError):
            # Bot not an admin in channel or invalid channel ID
            not_joined.append(ch)

    return len(not_joined) == 0, not_joined


def is_admin(user_id: int) -> bool:
    return user_id in config.ADMIN_IDS
