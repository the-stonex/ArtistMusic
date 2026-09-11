# ==========================================================
# Copyright (c) 2026 ArtistBots
# All Rights Reserved.
#
# Project      : ArtistBots API Telegram Music Bot
# Powered By   : Artist
# Type         : API Based Telegram Music Bot
#
# Bot          : @ArtistApibot
# Channel      : https://t.me/artistbots
# GitHub       : https://github.com/elevenyts/ArtistMusic
#
# Unauthorized copying, modification, or redistribution
# of this source code without permission is prohibited.
# ==========================================================

import logging

from pyrogram import enums, errors, filters, types

from ArtistMusic import app, config, db, lang
from ArtistMusic.helpers import buttons, utils


LOGGER = logging.getLogger(__name__)


# ==========================================================
# HELP
# ==========================================================

@app.on_message(filters.command(["help"]) & filters.private & ~app.bl_users)
@lang.language()
async def _help(_, m: types.Message):
    """Handle /help command in private chats."""

    try:
        await m.delete()
    except Exception:
        pass

    try:
        await m.reply_photo(
            photo=config.START_IMG,
            caption=m.lang["help_menu"],
            reply_markup=buttons.help_markup(m.lang),
            quote=True,
        )

    except Exception as photo_error:
        LOGGER.exception(
            "Help photo failed, using text fallback: %s",
            photo_error,
        )

        try:
            await m.reply_text(
                text=m.lang["help_menu"],
                reply_markup=buttons.help_markup(m.lang),
                quote=True,
            )
        except Exception as text_error:
            LOGGER.exception(
                "Help text fallback also failed: %s",
                text_error,
            )


# ==========================================================
# START
# ==========================================================

@app.on_message(filters.command(["start"]))
@lang.language()
async def start(_, message: types.Message):
    """Handle /start command."""

    # ------------------------------------------------------
    # Basic message validation
    # ------------------------------------------------------

    if not message:
        LOGGER.warning("Received empty message in /start handler")
        return

    if not message.chat:
        LOGGER.warning("Received /start without chat")
        return

    # ------------------------------------------------------
    # Delete /start command in groups
    # ------------------------------------------------------

    if message.chat.type != enums.ChatType.PRIVATE:
        try:
            await message.delete()
        except Exception as e:
            LOGGER.debug("Could not delete group /start message: %s", e)

    # ------------------------------------------------------
    # User validation
    # ------------------------------------------------------

    if not message.from_user:
        LOGGER.warning(
            "Cannot process /start: message.from_user is None"
        )
        return

    user_id = message.from_user.id

    # ------------------------------------------------------
    # Blacklisted user
    # ------------------------------------------------------

    try:
        if (
            user_id in app.bl_users
            and user_id not in db.notified
        ):
            return await message.reply_text(
                message.lang["bl_user_notify"]
            )

    except Exception as e:
        LOGGER.exception(
            "Blacklist check failed for user %s: %s",
            user_id,
            e,
        )

    # ------------------------------------------------------
    # /start help
    # ------------------------------------------------------

    try:
        if (
            len(message.command) > 1
            and message.command[1].lower() == "help"
        ):
            return await _help(_, message)

    except Exception as e:
        LOGGER.exception(
            "Failed while processing /start help: %s",
            e,
        )

    # ------------------------------------------------------
    # Chat type
    # ------------------------------------------------------

    private = message.chat.type == enums.ChatType.PRIVATE

    # ------------------------------------------------------
    # Start text
    # ------------------------------------------------------

    try:
        if private:
            _text = message.lang["start_pm"].format(
                message.from_user.first_name,
                app.name,
            )
        else:
            _text = message.lang["start_gp"].format(
                app.name,
            )

    except Exception as e:
        LOGGER.exception(
            "Failed to build start text: %s",
            e,
        )

        # Absolute fallback so /start can still respond
        first_name = (
            message.from_user.first_name
            or "there"
        )

        _text = (
            f"👋 Hello {first_name}!\n\n"
            f"🎵 Welcome to {app.name}\n\n"
            "Use the buttons below to continue."
        )

    # ------------------------------------------------------
    # Start buttons
    # ------------------------------------------------------

    key = None

    try:
        key = buttons.start_key(
            message.lang,
            private,
        )

    except Exception as e:
        LOGGER.exception(
            "Failed to create start buttons: %s",
            e,
        )

    # ------------------------------------------------------
    # Send START photo
    # ------------------------------------------------------

    photo_sent = False

    if config.START_IMG:
        try:
            await message.reply_photo(
                photo=config.START_IMG,
                caption=_text,
                reply_markup=key,
                quote=not private,
            )

            photo_sent = True

            LOGGER.info(
                "START photo sent successfully to user=%s chat=%s",
                user_id,
                message.chat.id,
            )

        except errors.ChatSendPhotosForbidden as e:
            LOGGER.warning(
                "Photo sending forbidden in chat %s: %s",
                message.chat.id,
                e,
            )

        except Exception as e:
            LOGGER.exception(
                "START photo failed in chat %s: %s",
                message.chat.id,
                e,
            )

    else:
        LOGGER.warning(
            "START_IMG is empty or not configured"
        )

    # ------------------------------------------------------
    # TEXT FALLBACK
    # ------------------------------------------------------

    if not photo_sent:
        try:
            await message.reply_text(
                text=_text,
                reply_markup=key,
                quote=not private,
            )

            LOGGER.info(
                "START text fallback sent successfully "
                "to user=%s chat=%s",
                user_id,
                message.chat.id,
            )

        except Exception as e:
            LOGGER.exception(
                "START text fallback FAILED "
                "for user=%s chat=%s: %s",
                user_id,
                message.chat.id,
                e,
            )

    # ------------------------------------------------------
    # Save private user
    # ------------------------------------------------------

    if private:
        try:
            if await db.is_user(user_id):
                return

        except Exception as e:
            LOGGER.exception(
                "Database user check failed for %s: %s",
                user_id,
                e,
            )

        try:
            await utils.send_log(message)
        except Exception as e:
            LOGGER.exception(
                "Failed to send user log for %s: %s",
                user_id,
                e,
            )

        try:
            await db.add_user(user_id)

            LOGGER.info(
                "New user added successfully: %s",
                user_id,
            )

        except Exception as e:
            LOGGER.exception(
                "Failed to add user %s to database: %s",
                user_id,
                e,
            )


# ==========================================================
# GROUP SETTINGS
# ==========================================================

@app.on_message(
    filters.command(["playmode", "settings"])
    & filters.group
    & ~app.bl_users
)
@lang.language()
async def settings(_, message: types.Message):
    """Handle /playmode or /settings command."""

    try:
        await message.delete()
    except Exception:
        pass

    try:
        admin_only = await db.get_play_mode(
            message.chat.id
        )

        force_admin = await db.get_force_mode(
            message.chat.id
        )

        _language = "en"

        await utils.safe_text(
            message,
            message.lang["start_settings"].format(
                message.chat.title
            ),
            reply_markup=buttons.settings_markup(
                message.lang,
                admin_only,
                force_admin,
                _language,
                message.chat.id,
            ),
            quote=True,
        )

    except Exception as e:
        LOGGER.exception(
            "Settings command failed in chat %s: %s",
            message.chat.id,
            e,
        )


# ==========================================================
# NEW GROUP MEMBER / BOT ADDED
# ==========================================================

@app.on_message(
    filters.new_chat_members,
    group=7,
)
@lang.language()
async def _new_member(_, message: types.Message):
    """Handle new member events - detect when bot is added."""

    try:
        if message.chat.type != enums.ChatType.SUPERGROUP:
            try:
                await message.chat.leave()
            except Exception as e:
                LOGGER.exception(
                    "Failed to leave unsupported chat %s: %s",
                    message.chat.id,
                    e,
                )
            return

        for member in message.new_chat_members:

            if member.id != app.id:
                continue

            try:
                if await db.is_chat(message.chat.id):
                    return

            except Exception as e:
                LOGGER.exception(
                    "Group database check failed for %s: %s",
                    message.chat.id,
                    e,
                )

            try:
                await db.add_chat(
                    message.chat.id
                )

                LOGGER.info(
                    "Bot added to new group: %s (%s)",
                    message.chat.title,
                    message.chat.id,
                )

            except Exception as e:
                LOGGER.exception(
                    "Failed to add group %s to database: %s",
                    message.chat.id,
                    e,
                )

    except Exception as e:
        LOGGER.exception(
            "New member handler failed: %s",
            e,
        )
