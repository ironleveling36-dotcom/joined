"""
User-facing handlers:
  /start  – welcome + force-join check
  verify  – re-check membership
  home / about / support callbacks
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message

import database
import keyboards
import messages
from utils import check_membership
import config

router = Router(name="user")


# ── /start ────────────────────────────────────────────────────────────────────
@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    user = message.from_user
    all_joined, _missing = await check_membership(message.bot, user.id)

    if not all_joined:
        # FIX: reuse the channels list already fetched inside check_membership
        # instead of making a second DB round-trip. We pass _missing if not empty,
        # else fall back to get_force_channels() (edge case: all channels ok but
        # list needed for UI, which won't happen here since all_joined=False).
        channels = await database.get_force_channels()
        await database.set_user_verified(user.id, False)
        await message.answer(
            messages.WELCOME.format(bot_name=config.BOT_NAME),
            reply_markup=keyboards.join_channels_kb(channels),
            parse_mode="HTML",
        )
        return

    await database.set_user_verified(user.id, True)
    await message.answer(
        messages.VERIFIED_SUCCESS,
        reply_markup=keyboards.verified_main_menu(),
        parse_mode="HTML",
    )


# ── Verify callback ───────────────────────────────────────────────────────────
@router.callback_query(F.data == "verify")
async def callback_verify(call: CallbackQuery) -> None:
    user = call.from_user
    all_joined, _missing = await check_membership(call.bot, user.id)

    if not all_joined:
        channels = await database.get_force_channels()
        await call.answer(
            "❌ You haven't joined all required channels.",
            show_alert=True,
        )
        try:
            await call.message.edit_reply_markup(
                reply_markup=keyboards.join_channels_kb(channels)
            )
        except Exception:
            pass
        return

    await database.set_user_verified(user.id, True)
    await call.answer("✅ Verified successfully!", show_alert=False)
    await call.message.edit_text(
        messages.VERIFIED_SUCCESS,
        reply_markup=keyboards.verified_main_menu(),
        parse_mode="HTML",
    )


# ── Gated menu guard ──────────────────────────────────────────────────────────
async def _guard(call: CallbackQuery) -> bool:
    """
    Returns True if user is verified.
    If not, sends alert + redirects to join screen, returns False.
    """
    verified = await database.is_user_verified(call.from_user.id)
    if not verified:
        channels = await database.get_force_channels()
        await call.answer("❌ You must join all channels first.", show_alert=True)
        try:
            await call.message.edit_text(
                messages.NOT_JOINED,
                reply_markup=keyboards.join_channels_kb(channels),
                parse_mode="HTML",
            )
        except Exception:
            pass
        return False
    return True


@router.callback_query(F.data == "home")
async def callback_home(call: CallbackQuery) -> None:
    if not await _guard(call):
        return
    await call.answer()
    await call.message.edit_text(
        messages.HOME,
        reply_markup=keyboards.verified_main_menu(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "about")
async def callback_about(call: CallbackQuery) -> None:
    if not await _guard(call):
        return
    await call.answer()
    await call.message.edit_text(
        messages.ABOUT,
        reply_markup=keyboards.verified_main_menu(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "support")
async def callback_support(call: CallbackQuery) -> None:
    if not await _guard(call):
        return
    await call.answer()
    await call.message.edit_text(
        messages.SUPPORT,
        reply_markup=keyboards.verified_main_menu(),
        parse_mode="HTML",
    )
