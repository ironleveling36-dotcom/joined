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


def _build_welcome_msg(template: str, user) -> str:
    """
    Render the welcome message template with the user's real info.
    Safely handles missing username or last_name.
    """
    username = f"@{user.username}" if user.username else "N/A"
    last_name = user.last_name or ""
    try:
        return template.format(
            first_name=user.first_name,
            last_name=last_name,
            username=username,
            user_id=user.id,
        )
    except KeyError:
        # If admin used an unknown placeholder, return template as-is
        return template


async def _send_welcome_message(bot, user) -> None:
    """
    Fetch the welcome message from DB (or use default) and send it to the user.
    Sends as a SEPARATE message after the verification success message.
    """
    template = await database.get_setting(
        messages.WELCOME_MSG_SETTING_KEY,
        default=messages.DEFAULT_WELCOME_MESSAGE,
    )
    if not template.strip():
        return  # admin cleared it — don't send anything

    text = _build_welcome_msg(template, user)
    try:
        await bot.send_message(
            chat_id=user.id,
            text=text,
            parse_mode="HTML",
        )
    except Exception:
        pass  # Don't crash verification if welcome message fails


# ── /start ────────────────────────────────────────────────────────────────────
@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    user = message.from_user
    all_joined, _missing = await check_membership(message.bot, user.id)

    if not all_joined:
        channels = await database.get_force_channels()
        await database.set_user_verified(user.id, False)
        await message.answer(
            messages.WELCOME.format(bot_name=config.BOT_NAME),
            reply_markup=keyboards.join_channels_kb(channels),
            parse_mode="HTML",
        )
        return

    # Check if already verified — don't send welcome message again on repeat /start
    already_verified = await database.is_user_verified(user.id)

    await database.set_user_verified(user.id, True)
    await message.answer(
        messages.VERIFIED_SUCCESS,
        reply_markup=keyboards.verified_main_menu(),
        parse_mode="HTML",
    )

    # Send welcome message only on first-time verification
    if not already_verified:
        await _send_welcome_message(message.bot, user)


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

    # Check if already verified — don't send welcome message again
    already_verified = await database.is_user_verified(user.id)

    await database.set_user_verified(user.id, True)
    await call.answer("✅ Verified successfully!", show_alert=False)
    await call.message.edit_text(
        messages.VERIFIED_SUCCESS,
        reply_markup=keyboards.verified_main_menu(),
        parse_mode="HTML",
    )

    # Send welcome message only on first-time verification
    if not already_verified:
        await _send_welcome_message(call.bot, user)


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
