"""
Admin handlers:
  /admin  – open admin panel
  Stats, Broadcast, Add/Remove channel, Block user
  /debug  – live membership check debug tool
"""
from __future__ import annotations

import asyncio
import functools
import logging

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from aiogram.exceptions import TelegramAPIError

import config
import database
import keyboards
import messages
from utils import is_admin

logger = logging.getLogger(__name__)

router = Router(name="admin")


# ── States ─────────────────────────────────────────────────────────────────────
class AdminState(StatesGroup):
    waiting_add_channel    = State()
    waiting_remove_channel = State()
    waiting_block_user     = State()
    waiting_broadcast_type = State()
    waiting_broadcast_msg  = State()
    waiting_broadcast_confirm = State()
    waiting_welcome_msg    = State()


# ── Guard decorators ──────────────────────────────────────────────────────────
# FIX: added @functools.wraps(handler) so aiogram can properly inspect the
# original handler signature and inject FSMContext / other dependencies.

def _admin_only_msg(handler):
    @functools.wraps(handler)
    async def wrapper(message: Message, *args, **kwargs):
        if not is_admin(message.from_user.id):
            await message.answer(messages.NOT_ADMIN)
            return
        await handler(message, *args, **kwargs)
    return wrapper


def _admin_only_cb(handler):
    @functools.wraps(handler)
    async def wrapper(call: CallbackQuery, *args, **kwargs):
        if not is_admin(call.from_user.id):
            await call.answer(messages.NOT_ADMIN, show_alert=True)
            return
        await handler(call, *args, **kwargs)
    return wrapper


# ── /admin command ─────────────────────────────────────────────────────────────
@router.message(Command("admin"))
@_admin_only_msg
async def cmd_admin(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        messages.ADMIN_WELCOME.format(name=message.from_user.first_name),
        reply_markup=keyboards.admin_panel_kb(),
        parse_mode="HTML",
    )


# ── Stats ──────────────────────────────────────────────────────────────────────
@router.callback_query(F.data == "adm_stats")
@_admin_only_cb
async def callback_stats(call: CallbackQuery) -> None:
    await call.answer()
    counts   = await database.get_user_count()
    channels = await database.get_force_channels()
    await call.message.edit_text(
        messages.STATS_TEMPLATE.format(
            total=counts["total"],
            verified=counts["verified"],
            channels=len(channels),
        ),
        reply_markup=keyboards.back_to_admin_kb(),
        parse_mode="HTML",
    )


# ── List channels ──────────────────────────────────────────────────────────────
@router.callback_query(F.data == "adm_list_channels")
@_admin_only_cb
async def callback_list_channels(call: CallbackQuery) -> None:
    await call.answer()
    channels = await database.get_force_channels()
    if not channels:
        text = "📋 <b>No force-join channels configured.</b>"
    else:
        lines = ["📋 <b>Force-Join Channels</b>\n"]
        for i, ch in enumerate(channels, 1):
            lines.append(
                f"{i}. <b>{ch.channel_name}</b>\n"
                f"   ID: <code>{ch.channel_id}</code>\n"
                f"   Link: {ch.channel_link}"
            )
        text = "\n".join(lines)
    await call.message.edit_text(
        text,
        reply_markup=keyboards.back_to_admin_kb(),
        parse_mode="HTML",
    )


# ── Add channel ────────────────────────────────────────────────────────────────
@router.callback_query(F.data == "adm_add_channel")
@_admin_only_cb
async def callback_add_channel(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer()
    await state.set_state(AdminState.waiting_add_channel)
    await call.message.edit_text(
        messages.ADD_CHANNEL_INSTRUCTIONS,
        reply_markup=keyboards.back_to_admin_kb(),
        parse_mode="HTML",
    )


@router.message(AdminState.waiting_add_channel)
async def process_add_channel(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        return

    # FIX: message.text can be None if admin sent a photo/sticker/etc.
    if not message.text:
        await message.answer(
            "⚠️ Please send a <b>text</b> message in the required format.",
            parse_mode="HTML",
        )
        return

    raw = message.text.strip()
    parts = [p.strip() for p in raw.split("|")]
    if len(parts) != 3:
        await message.answer(
            "⚠️ Invalid format. Use:\n<code>CHANNEL_ID | https://t.me/channel | Channel Name</code>",
            parse_mode="HTML",
        )
        return

    channel_id, channel_link, channel_name = parts

    # Basic link sanity check
    if not channel_link.startswith("https://t.me/") and not channel_link.startswith("https://t.me/+"):
        await message.answer(
            "⚠️ Channel link must start with <code>https://t.me/</code>",
            parse_mode="HTML",
        )
        return

    ok = await database.add_force_channel(channel_id, channel_link, channel_name)
    await state.clear()
    if ok:
        await message.answer(
            f"✅ Channel <b>{channel_name}</b> added successfully.",
            reply_markup=keyboards.admin_panel_kb(),
            parse_mode="HTML",
        )
    else:
        await message.answer(
            "⚠️ Channel already exists.",
            reply_markup=keyboards.admin_panel_kb(),
            parse_mode="HTML",
        )


# ── Remove channel ─────────────────────────────────────────────────────────────
@router.callback_query(F.data == "adm_rem_channel")
@_admin_only_cb
async def callback_rem_channel(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer()
    await state.set_state(AdminState.waiting_remove_channel)
    await call.message.edit_text(
        messages.REMOVE_CHANNEL_INSTRUCTIONS,
        reply_markup=keyboards.back_to_admin_kb(),
        parse_mode="HTML",
    )


@router.message(AdminState.waiting_remove_channel)
async def process_remove_channel(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        return

    # FIX: guard against non-text messages
    if not message.text:
        await message.answer("⚠️ Please send the channel ID as text.")
        return

    channel_id = message.text.strip()
    ok = await database.remove_force_channel(channel_id)
    await state.clear()
    if ok:
        await message.answer(
            f"✅ Channel <code>{channel_id}</code> removed.",
            reply_markup=keyboards.admin_panel_kb(),
            parse_mode="HTML",
        )
    else:
        await message.answer(
            f"⚠️ Channel <code>{channel_id}</code> not found.",
            reply_markup=keyboards.admin_panel_kb(),
            parse_mode="HTML",
        )


# ── Block user ─────────────────────────────────────────────────────────────────
@router.callback_query(F.data == "adm_block_user")
@_admin_only_cb
async def callback_block_user(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer()
    await state.set_state(AdminState.waiting_block_user)
    await call.message.edit_text(
        messages.BLOCK_USER_INSTRUCTIONS,
        reply_markup=keyboards.back_to_admin_kb(),
        parse_mode="HTML",
    )


@router.message(AdminState.waiting_block_user)
async def process_block_user(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        return

    # FIX: guard against non-text messages
    if not message.text:
        await message.answer("⚠️ Please send the user ID as text.")
        return

    raw = message.text.strip()
    if not raw.lstrip("-").isdigit():
        await message.answer("⚠️ Invalid user ID. Must be a number.")
        return

    uid = int(raw)
    await database.block_user(uid)
    await state.clear()
    await message.answer(
        f"🚫 User <code>{uid}</code> has been blocked.",
        reply_markup=keyboards.admin_panel_kb(),
        parse_mode="HTML",
    )


# ── Broadcast ──────────────────────────────────────────────────────────────────
@router.callback_query(F.data == "adm_broadcast")
@_admin_only_cb
async def callback_broadcast(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer()
    await state.set_state(AdminState.waiting_broadcast_type)
    await call.message.edit_text(
        messages.BROADCAST_CHOOSE_TYPE,
        reply_markup=keyboards.broadcast_type_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data.in_({"bc_text", "bc_photo", "bc_video", "bc_document"}))
@_admin_only_cb
async def callback_broadcast_type(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer()
    # bc_text → text, bc_photo → photo, etc.
    bc_type = call.data[3:]   # strip "bc_" prefix cleanly
    await state.update_data(bc_type=bc_type)
    await state.set_state(AdminState.waiting_broadcast_msg)

    type_hints = {
        "text":     "✉️ Send the <b>text</b> message to broadcast.",
        "photo":    "🖼 Send the <b>photo</b> (with optional caption) to broadcast.",
        "video":    "🎥 Send the <b>video</b> (with optional caption) to broadcast.",
        "document": "📄 Send the <b>document</b> (with optional caption) to broadcast.",
    }
    await call.message.edit_text(
        type_hints.get(bc_type, "Send the message."),
        reply_markup=keyboards.back_to_admin_kb(),
        parse_mode="HTML",
    )


@router.message(AdminState.waiting_broadcast_msg)
async def process_broadcast_message(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        return

    data = await state.get_data()
    bc_type = data.get("bc_type", "text")

    await state.update_data(message_id=message.message_id, chat_id=message.chat.id)
    await state.set_state(AdminState.waiting_broadcast_confirm)

    count = await database.get_user_count()
    preview = message.text or message.caption or f"[{bc_type.upper()} FILE]"
    await message.answer(
        messages.BROADCAST_PREVIEW.format(
            preview=preview[:300],
            count=count["verified"],
        ),
        reply_markup=keyboards.confirm_broadcast_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "bc_confirm")
@_admin_only_cb
async def callback_broadcast_confirm(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer("📤 Broadcasting…")
    data = await state.get_data()
    await state.clear()

    # FIX: use .get() with fallback — avoids KeyError if state was lost (bot restart etc.)
    msg_id    = data.get("message_id")
    from_chat = data.get("chat_id")

    if not msg_id or not from_chat:
        await call.message.edit_text(
            "⚠️ Broadcast data was lost (bot may have restarted). Please start over.",
            reply_markup=keyboards.back_to_admin_kb(),
            parse_mode="HTML",
        )
        return

    users = await database.get_all_verified_users()
    sent = failed = 0

    status_msg = await call.message.edit_text(
        f"📤 Broadcasting to <b>{len(users)}</b> users…",
        parse_mode="HTML",
    )

    for uid in users:
        try:
            await call.bot.copy_message(
                chat_id=uid,
                from_chat_id=from_chat,
                message_id=msg_id,
            )
            sent += 1
        except Exception:
            failed += 1
        await asyncio.sleep(config.BROADCAST_DELAY)

    await database.log_broadcast(call.from_user.id, str(msg_id), sent, failed)
    await status_msg.edit_text(
        messages.BROADCAST_DONE.format(sent=sent, failed=failed),
        reply_markup=keyboards.back_to_admin_kb(),
        parse_mode="HTML",
    )


# ── Welcome Message Management ────────────────────────────────────────────────

def _render_preview(template: str, name: str = "John") -> str:
    """Render a preview using placeholder values."""
    try:
        return template.format(
            first_name=name,
            last_name="Doe",
            username="@johndoe",
            user_id="123456789",
        )
    except KeyError as e:
        return f"⚠️ Unknown placeholder: {e}\n\n{template}"


@router.callback_query(F.data == "adm_welcome_msg")
@_admin_only_cb
async def callback_welcome_msg(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer()
    await state.clear()
    current = await database.get_setting(
        messages.WELCOME_MSG_SETTING_KEY,
        default=messages.DEFAULT_WELCOME_MESSAGE,
    )
    await call.message.edit_text(
        messages.WELCOME_MSG_PANEL.format(current=current),
        reply_markup=keyboards.welcome_msg_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "wm_edit")
@_admin_only_cb
async def callback_wm_edit(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer()
    await state.set_state(AdminState.waiting_welcome_msg)
    await call.message.edit_text(
        messages.WELCOME_MSG_INSTRUCTIONS,
        reply_markup=keyboards.back_to_admin_kb(),
        parse_mode="HTML",
    )


@router.message(AdminState.waiting_welcome_msg)
async def process_welcome_msg(message: Message, state: FSMContext) -> None:
    if not is_admin(message.from_user.id):
        return

    if not message.text:
        await message.answer("⚠️ Please send a text message for the welcome message.")
        return

    new_msg = message.text.strip()
    preview = _render_preview(new_msg, name=message.from_user.first_name)

    # Store draft in FSM, ask for confirmation
    await state.update_data(welcome_msg_draft=new_msg)
    await state.set_state(None)  # clear FSM state but keep data

    await message.answer(
        messages.WELCOME_MSG_PREVIEW.format(preview=preview),
        reply_markup=keyboards.confirm_welcome_msg_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "wm_save")
@_admin_only_cb
async def callback_wm_save(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer()
    data = await state.get_data()
    draft = data.get("welcome_msg_draft")

    if not draft:
        await call.answer("⚠️ No draft found. Please edit the message first.", show_alert=True)
        return

    await database.set_setting(messages.WELCOME_MSG_SETTING_KEY, draft)
    await state.clear()
    await call.message.edit_text(
        messages.WELCOME_MSG_SAVED,
        reply_markup=keyboards.welcome_msg_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "wm_preview")
@_admin_only_cb
async def callback_wm_preview(call: CallbackQuery) -> None:
    await call.answer()
    current = await database.get_setting(
        messages.WELCOME_MSG_SETTING_KEY,
        default=messages.DEFAULT_WELCOME_MESSAGE,
    )
    preview = _render_preview(current, name=call.from_user.first_name)
    await call.message.edit_text(
        messages.WELCOME_MSG_PREVIEW.format(preview=preview),
        reply_markup=keyboards.welcome_msg_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "wm_reset")
@_admin_only_cb
async def callback_wm_reset(call: CallbackQuery) -> None:
    await call.answer()
    await call.message.edit_text(
        "🔄 <b>Reset Welcome Message</b>\n\nAre you sure you want to reset to the default message?",
        reply_markup=keyboards.confirm_reset_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "wm_reset_confirm")
@_admin_only_cb
async def callback_wm_reset_confirm(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer()
    await state.clear()
    await database.set_setting(
        messages.WELCOME_MSG_SETTING_KEY,
        messages.DEFAULT_WELCOME_MESSAGE,
    )
    await call.message.edit_text(
        messages.WELCOME_MSG_RESET,
        reply_markup=keyboards.welcome_msg_kb(),
        parse_mode="HTML",
    )


# ── Debug command ─────────────────────────────────────────────────────────────
@router.message(Command("debug"))
@_admin_only_msg
async def cmd_debug(message: Message) -> None:
    """
    Live membership check for the admin themselves.
    Shows exactly what Telegram returns for each configured channel.
    Use this when users report 'not joined' even after joining.
    """
    uid = message.from_user.id
    channels = await database.get_force_channels()

    if not channels:
        await message.answer("⚠️ No force-join channels configured.")
        return

    lines = [f"🔍 <b>Debug: Membership Check</b>\nUser ID: <code>{uid}</code>\n"]

    for ch in channels:
        # Normalize channel_id to int
        try:
            chat_id = int(ch.channel_id)
        except ValueError:
            chat_id = ch.channel_id

        try:
            member = await message.bot.get_chat_member(chat_id=chat_id, user_id=uid)
            status = member.status
            emoji = "✅" if status in ("member", "administrator", "creator") else "❌"
            lines.append(
                f"{emoji} <b>{ch.channel_name}</b>\n"
                f"   ID: <code>{ch.channel_id}</code>\n"
                f"   Status: <code>{status}</code>"
            )
        except TelegramAPIError as e:
            error_text = str(e)
            if "CHAT_ADMIN_REQUIRED" in error_text or "Forbidden" in error_text:
                hint = "⚠️ Bot is NOT admin in this channel!"
            elif "chat not found" in error_text.lower():
                hint = "⚠️ Wrong channel ID — channel not found!"
            elif "user not found" in error_text.lower():
                hint = "⚠️ User not found in Telegram's records."
            else:
                hint = f"⚠️ API Error: {error_text}"
            lines.append(
                f"🔴 <b>{ch.channel_name}</b>\n"
                f"   ID: <code>{ch.channel_id}</code>\n"
                f"   {hint}"
            )

    lines.append(
        "\n<b>Common fixes:</b>\n"
        "• Make the bot <b>admin</b> in each channel\n"
        "• Use numeric ID like <code>-1001234567890</code>\n"
        "• For public channels you can also use <code>@username</code>"
    )

    await message.answer("\n".join(lines), parse_mode="HTML")


# ── Back to panel / Close ──────────────────────────────────────────────────────
@router.callback_query(F.data == "adm_panel")
@_admin_only_cb
async def callback_adm_panel(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer()
    await state.clear()
    await call.message.edit_text(
        messages.ADMIN_WELCOME.format(name=call.from_user.first_name),
        reply_markup=keyboards.admin_panel_kb(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "adm_close")
@_admin_only_cb
async def callback_adm_close(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer()
    await state.clear()
    try:
        await call.message.delete()
    except Exception:
        pass
