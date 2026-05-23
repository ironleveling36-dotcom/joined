"""
All InlineKeyboardMarkup builders live here.
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import ForceChannel


def join_channels_kb(channels: list[ForceChannel]) -> InlineKeyboardMarkup:
    """Channels list + Verify button."""
    builder = InlineKeyboardBuilder()
    for ch in channels:
        builder.row(
            InlineKeyboardButton(
                text=f"📢 {ch.channel_name}",
                url=ch.channel_link,
            )
        )
    builder.row(
        InlineKeyboardButton(
            text="✅ I've Joined – Verify Me",
            callback_data="verify",
        )
    )
    return builder.as_markup()


def verified_main_menu() -> InlineKeyboardMarkup:
    """Main menu shown to verified users."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🏠 Home",        callback_data="home"),
        InlineKeyboardButton(text="ℹ️ About",       callback_data="about"),
    )
    builder.row(
        InlineKeyboardButton(text="📞 Support",     callback_data="support"),
        InlineKeyboardButton(text="🔄 Re-verify",   callback_data="verify"),
    )
    return builder.as_markup()


# ── Admin panel keyboards ──────────────────────────────────────────────────────
def admin_panel_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📢 Broadcast",         callback_data="adm_broadcast"),
        InlineKeyboardButton(text="📊 Stats",             callback_data="adm_stats"),
    )
    builder.row(
        InlineKeyboardButton(text="➕ Add Channel",       callback_data="adm_add_channel"),
        InlineKeyboardButton(text="➖ Remove Channel",    callback_data="adm_rem_channel"),
    )
    builder.row(
        InlineKeyboardButton(text="📋 List Channels",     callback_data="adm_list_channels"),
        InlineKeyboardButton(text="🚫 Block User",        callback_data="adm_block_user"),
    )
    builder.row(
        InlineKeyboardButton(text="✏️ Welcome Message",   callback_data="adm_welcome_msg"),
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Close Panel",       callback_data="adm_close"),
    )
    return builder.as_markup()


def broadcast_type_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✉️ Text",       callback_data="bc_text"),
        InlineKeyboardButton(text="🖼 Photo",       callback_data="bc_photo"),
    )
    builder.row(
        InlineKeyboardButton(text="🎥 Video",      callback_data="bc_video"),
        InlineKeyboardButton(text="📄 Document",   callback_data="bc_document"),
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Cancel",     callback_data="adm_close"),
    )
    return builder.as_markup()


def confirm_broadcast_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Send Now",   callback_data="bc_confirm"),
        InlineKeyboardButton(text="❌ Cancel",     callback_data="adm_close"),
    )
    return builder.as_markup()


def welcome_msg_kb() -> InlineKeyboardMarkup:
    """Welcome message management panel."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✏️ Edit Message",    callback_data="wm_edit"),
        InlineKeyboardButton(text="👁 Preview",         callback_data="wm_preview"),
    )
    builder.row(
        InlineKeyboardButton(text="🔄 Reset to Default", callback_data="wm_reset"),
    )
    builder.row(
        InlineKeyboardButton(text="🔙 Admin Panel",     callback_data="adm_panel"),
    )
    return builder.as_markup()


def confirm_welcome_msg_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Save",       callback_data="wm_save"),
        InlineKeyboardButton(text="✏️ Re-edit",    callback_data="wm_edit"),
        InlineKeyboardButton(text="❌ Cancel",     callback_data="adm_welcome_msg"),
    )
    return builder.as_markup()


def confirm_reset_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Yes, Reset", callback_data="wm_reset_confirm"),
        InlineKeyboardButton(text="❌ Cancel",     callback_data="adm_welcome_msg"),
    )
    return builder.as_markup()


def back_to_admin_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔙 Admin Panel", callback_data="adm_panel"))
    return builder.as_markup()
