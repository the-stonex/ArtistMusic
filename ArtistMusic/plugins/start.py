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

from pyrogram import enums, filters, types

from ArtistMusic import app, config, db, lang
from ArtistMusic.helpers import buttons, utils


LOGGER = logging.getLogger(__name__)


# ==========================================================
# HELP COMMAND
# ==========================================================

@app.on_message(
    filters.command("help")
    & filters.private
    & ~app.bl_users
)
@lang.language()
async def _help(_, message: types.Message):
    """Handle /help command in private chats."""

    try:
        await message.delete()
    except Exception:
        pass

    try:
        markup = buttons.help_markup(message.lang)
    except Exception as e:
        LOGGER.exception("Failed to create help buttons: %s", e)
        markup = None

    try:
        await message.reply_photo(
            photo=config.START_IMG,
            caption=message.lang["help_menu"],
            reply_markup=markup,
            quote=True,
        )

        LOGGER.info(
            "Help menu sent successfully to user %s",
            message.from_user.id if message.from_user else "unknown",
        )

    except Exception as e:
        LOGGER.exception(
            "Help photo failed, using text fallback: %s",
            e,
        )

        try:
            await message.reply_text(
                text=message.lang["help_menu"],
                reply_markup=markup,
                quote=True,
            )

            LOGGER.info("Help text fallback sent successfully.")

        except Exception as e2:
            LOGGER.exception(
                "Help text fallback failed: %s",
                e2,
            )


# ==========================================================
# START COMMAND
# ==========================================================

@app.on_message(filters.command("start"))
@lang.language()
async def start(_, message: types.Message):
    """Handle /start command."""

    try:
        if not message or not message.chat:
            LOGGER.error("Invalid /start message received.")
            return

        if not message.from_user:
            LOGGER.warning(
                "Ignoring /start because from_user is missing."
            )
            return

        user_id = message.from_user.id
        chat_id = message.chat.id
        private = message.chat.type == enums.ChatType.PRIVATE

        LOGGER.info(
            "Processing /start | user=%s | chat=%s | private=%s",
            user_id,
            chat_id,
            private,
        )

        # --------------------------------------------------
        # Delete command in groups
        # --------------------------------------------------

        if not private:
            try:
                await message.delete()
            except Exception as e:
                LOGGER.warning(
                    "Could not delete group /start message: %s",
                    e,
                )

        # --------------------------------------------------
        # Blacklisted user
        # --------------------------------------------------

        try:
            if (
                user_id in app.bl_users
                and user_id not in db.notified
            ):
                await message.reply_text(
                    message.lang["bl_user_notify"]
                )
                return

        except Exception as e:
            LOGGER.exception(
                "Blacklist check failed for user %s: %s",
                user_id,
                e,
            )

        # --------------------------------------------------
        # /start help
        # --------------------------------------------------

        try:
            if (
                len(message.command) > 1
                and message.command[1].lower() == "help"
            ):
                await _help(_, message)
                return

        except Exception as e:
            LOGGER.exception(
                "Failed to process /start help: %s",
                e,
            )

        # --------------------------------------------------
        # Start text
        # --------------------------------------------------

        try:
            if private:
                start_text = message.lang["start_pm"].format(
                    message.from_user.first_name,
                    app.name,
                )
            else:
                start_text = message.lang["start_gp"].format(
                    app.name,
                )

        except Exception as e:
            LOGGER.exception(
                "Failed to create start text: %s",
                e,
            )

            first_name = (
                message.from_user.first_name
                or "there"
            )

            start_text = (
                f"👋 Hello {first_name}!\n\n"
                f"🎵 Welcome to {app.name}\n\n"
                "Use the buttons below to continue."
            )

        # --------------------------------------------------
        # Start buttons
        # --------------------------------------------------

        try:
            start_markup = buttons.start_key(
                message.lang,
                private,
            )

        except Exception as e:
            LOGGER.exception(
                "Failed to create start buttons: %s",
                e,
            )
            start_markup = None

        # --------------------------------------------------
        # Send START PHOTO
        # --------------------------------------------------

        sent = False

        try:
            if config.START_IMG:
                await message.reply_photo(
                    photo=config.START_IMG,
                    caption=start_text,
                    reply_markup=start_markup,
                    quote=not private,
                )

                sent = True

                LOGGER.info(
                    "START photo sent successfully | user=%s | chat=%s",
                    user_id,
                    chat_id,
                )

            else:
                LOGGER.warning(
                    "START_IMG is empty/not configured."
                )

        except Exception as e:
            LOGGER.exception(
                "START photo failed | user=%s | chat=%s | error=%s",
                user_id,
                chat_id,
                e,
            )

        # --------------------------------------------------
        # TEXT FALLBACK
        # --------------------------------------------------

        if not sent:
            try:
                await message.reply_text(
                    text=start_text,
                    reply_markup=start_markup,
                    quote=not private,
                )

                sent = True

                LOGGER.info(
                    "START text fallback sent successfully | "
                    "user=%s | chat=%s",
                    user_id,
                    chat_id,
                )

            except Exception as e:
                LOGGER.exception(
                    "START text fallback FAILED | "
                    "user=%s | chat=%s | error=%s",
                    user_id,
                    chat_id,
                    e,
                )

        # --------------------------------------------------
        # Save user
        # --------------------------------------------------

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
                return

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
                    "User added successfully to database: %s",
                    user_id,
                )

            except Exception as e:
                LOGGER.exception(
                    "Failed to add user %s: %s",
                    user_id,
                    e,
                )

    except Exception as e:
        LOGGER.exception(
            "UNHANDLED /start ERROR: %s",
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
    """Handle /playmode and /settings."""

    try:
        try:
            await message.delete()
        except Exception:
            pass

        admin_only = await db.get_play_mode(
            message.chat.id
        )

        force_admin = await db.get_force_mode(
            message.chat.id
        )

        markup = buttons.settings_markup(
            message.lang,
            admin_only,
            force_admin,
            "en",
            message.chat.id,
        )

        await utils.safe_text(
            message,
            message.lang["start_settings"].format(
                message.chat.title
            ),
            reply_markup=markup,
            quote=True,
        )

    except Exception as e:
        LOGGER.exception(
            "Settings command failed in chat %s: %s",
            message.chat.id,
            e,
        )


# ==========================================================
# BOT ADDED TO GROUP
# ==========================================================

@app.on_message(
    filters.new_chat_members,
    group=7,
)
@lang.language()
async def _new_member(_, message: types.Message):
    """Handle bot being added to a group."""

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

            LOGGER.info(
                "Bot added to group: %s | %s",
                message.chat.title,
                message.chat.id,
            )

            try:
                if await db.is_chat(message.chat.id):
                    return

            except Exception as e:
                LOGGER.exception(
                    "Group database check failed: %s",
                    e,
                )
                return

            try:
                await db.add_chat(message.chat.id)

                LOGGER.info(
                    "Group added successfully: %s",
                    message.chat.id,
                )

            except Exception as e:
                LOGGER.exception(
                    "Failed to save group %s: %s",
                    message.chat.id,
                    e,
                )

            return

    except Exception as e:
        LOGGER.exception(
            "New member handler failed: %s",
            e,
        )
