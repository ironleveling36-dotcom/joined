"""
Utility helpers.
"""
from __future__ import annotations

import logging

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError, TelegramAPIError

from database import ForceChannel, get_force_channels
import config

logger = logging.getLogger(__name__)

# Statuses that mean the user is NOT in the channel
NOT_MEMBER_STATUSES = ("left", "kicked")


async def check_membership(bot: Bot, user_id: int) -> tuple[bool, list[ForceChannel]]:
    """
    Returns (all_joined: bool, not_joined_channels: list[ForceChannel]).
    Logs exactly what status Telegram returns for each channel — helps debug.
    """
    channels = await get_force_channels()
    if not channels:
        return True, []

    not_joined: list[ForceChannel] = []

    for ch in channels:
        # Normalize channel_id: always pass as int if it's a numeric string
        try:
            chat_id = int(ch.channel_id)
        except ValueError:
            # Username format like @mychannel — pass as-is
            chat_id = ch.channel_id

        try:
            member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
            status = member.status

            logger.info(
                f"[MemberCheck] user={user_id} channel={ch.channel_id}({ch.channel_name}) "
                f"→ status={status}"
            )

            if status in NOT_MEMBER_STATUSES:
                not_joined.append(ch)

        except TelegramForbiddenError as e:
            # Bot is NOT an admin in the channel or was kicked from it
            logger.warning(
                f"[MemberCheck] FORBIDDEN for channel={ch.channel_id}({ch.channel_name}): {e}. "
                f"Make sure the bot is an ADMIN in that channel."
            )
            not_joined.append(ch)

        except TelegramBadRequest as e:
            # Invalid channel ID or user not found
            logger.warning(
                f"[MemberCheck] BAD_REQUEST for channel={ch.channel_id}({ch.channel_name}): {e}. "
                f"Check that channel_id is correct (use numeric ID like -1001234567890)."
            )
            not_joined.append(ch)

        except TelegramAPIError as e:
            # Any other Telegram API error
            logger.error(
                f"[MemberCheck] API_ERROR for channel={ch.channel_id}({ch.channel_name}): {e}"
            )
            not_joined.append(ch)

        except Exception as e:
            logger.error(
                f"[MemberCheck] UNEXPECTED error for channel={ch.channel_id}: {e}"
            )
            not_joined.append(ch)

    return len(not_joined) == 0, not_joined


def is_admin(user_id: int) -> bool:
    return user_id in config.ADMIN_IDS
