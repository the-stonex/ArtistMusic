# ==========================================================
# ArtistMusic - Fixed Start Plugin
# ==========================================================

from pyrogram import enums, errors, filters, types
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from ArtistMusic import app, config, db, lang, logger
from ArtistMusic.helpers import buttons, utils


# ==========================================================
# FIXED START BUTTONS
# ==========================================================

def fixed_start_key(language, private=True):
    """
    Fixed start menu keyboard.

    Layout:
    1. ADD ME TO YOUR GROUP
    2. HELP
    3. SUPPORT | CHANNEL
    4. LANGUAGE | DEVELOPER
    """

    # Bot username
    bot_username = getattr(app, "username", None)

    if not bot_username:
        bot_username = getattr(app, "name", "ArtistMusic")

    bot_username = str(bot_username).replace("@", "").strip()

    # Support / Channel
    support_url = getattr(
        config,
        "SUPPORT_CHAT",
        "https://t.me/Artistbots"
    )

    channel_url = getattr(
        config,
        "SUPPORT_CHANNEL",
        "https://t.me/Elevenytschats"
    )

    # Developer
    developer_url = "https://github.com/the-stonex"

    # Add to group
    add_group_url = (
        f"https://t.me/{bot_username}?startgroup=true"
    )

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "➕ ADD ME TO YOUR GROUP",
                    url=add_group_url
                )
            ],

            [
                InlineKeyboardButton(
                    "❓ HELP",
                    callback_data="help"
                )
            ],

            [
                InlineKeyboardButton(
                    "↗️ SUPPORT",
                    url=support_url
                ),
                InlineKeyboardButton(
                    "↗️ CHANNEL",
                    url=channel_url
                )
            ],

            [
                InlineKeyboardButton(
                    "🌐 LANGUAGE",
                    callback_data="help_langs"
                ),
                InlineKeyboardButton(
                    "↗️ DEVELOPER",
                    url=developer_url
                )
            ]
        ]
    )


# ==========================================================
# IMPORTANT:
# Existing callbacks.py uses buttons.start_key()
# So replace that method with our fixed version.
# ==========================================================

buttons.start_key = fixed_start_key


# ==========================================================
# HELP
# ==========================================================

@app.on_message(
    filters.command(["help"])
    & filters.private
    & ~app.bl_users
)
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

        logger.warning(
            f"Start image failed in /help: {photo_error}"
        )

        try:
            await m.reply_text(
                text=m.lang["help_menu"],
                reply_markup=buttons.help_markup(m.lang),
                quote=True,
            )
        except Exception as text_error:
            logger.error(
                f"Help menu failed: {text_error}",
                exc_info=True
            )


# ==========================================================
# START
# ==========================================================

@app.on_message(filters.command(["start"]))
@lang.language()
async def start(_, message: types.Message):
    """Handle /start command."""

    # ------------------------------------------------------
    # Delete /start in groups
    # ------------------------------------------------------

    if message.chat.type != enums.ChatType.PRIVATE:
        try:
            await message.delete()
        except Exception:
            pass

    # ------------------------------------------------------
    # User check
    # ------------------------------------------------------

    if not message.from_user:
        return

    # ------------------------------------------------------
    # Blacklisted user
    # ------------------------------------------------------

    if (
        message.from_user.id in app.bl_users
        and message.from_user.id not in db.notified
    ):
        return await message.reply_text(
            message.lang["bl_user_notify"]
        )

    # ------------------------------------------------------
    # /start help
    # ------------------------------------------------------

    if (
        len(message.command) > 1
        and message.command[1].lower() == "help"
    ):
        return await _help(_, message)

    # ------------------------------------------------------
    # Private / Group
    # ------------------------------------------------------

    private = (
        message.chat.type == enums.ChatType.PRIVATE
    )

    # ------------------------------------------------------
    # Start text
    # ------------------------------------------------------

    try:
        _text = (
            message.lang["start_pm"].format(
                message.from_user.first_name,
                app.name
            )
            if private
            else
            message.lang["start_gp"].format(
                app.name
            )
        )

    except Exception:
        _text = (
            f"👋 <b>Hey {message.from_user.first_name}</b>\n\n"
            f"🎵 <b>{app.name}</b>\n\n"
            f"🎶 Smooth and lag free music bot"
        )

    # ------------------------------------------------------
    # Build buttons safely
    # ------------------------------------------------------

    try:
        key = fixed_start_key(
            message.lang,
            private
        )

    except Exception as button_error:

        logger.error(
            f"Start button error: {button_error}",
            exc_info=True
        )

        key = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "❓ HELP",
                        callback_data="help"
                    )
                ]
            ]
        )

    # ------------------------------------------------------
    # IMAGE 1
    # ------------------------------------------------------

    start_image = getattr(
        config,
        "START_IMG",
        None
    )

    if not start_image:
        start_image = getattr(
            config,
            "DEFAULT_THUMB",
            None
        )

    # ------------------------------------------------------
    # Try START_IMG
    # ------------------------------------------------------

    try:

        if start_image:

            await message.reply_photo(
                photo=start_image,
                caption=_text,
                reply_markup=key,
                quote=not private,
            )

        else:

            raise ValueError(
                "START_IMG is empty"
            )

    # ------------------------------------------------------
    # Photo forbidden / unavailable
    # ------------------------------------------------------

    except errors.ChatSendPhotosForbidden:

        try:

            await message.reply_text(
                text=_text,
                reply_markup=key,
                quote=not private,
            )

        except Exception as text_error:

            logger.error(
                f"Start text failed: {text_error}",
                exc_info=True
            )

    # ------------------------------------------------------
    # IMAGE ERROR
    # ------------------------------------------------------

    except Exception as image_error:

        logger.error(
            f"START_IMG failed: {image_error}",
            exc_info=True
        )

        # --------------------------------------------------
        # Try default image
        # --------------------------------------------------

        default_image = getattr(
            config,
            "DEFAULT_THUMB",
            None
        )

        if (
            default_image
            and default_image != start_image
        ):

            try:

                await message.reply_photo(
                    photo=default_image,
                    caption=_text,
                    reply_markup=key,
                    quote=not private,
                )

            except Exception as default_error:

                logger.error(
                    f"Default start image failed: "
                    f"{default_error}",
                    exc_info=True
                )

                # ------------------------------------------
                # Final fallback: TEXT + BUTTONS
                # ------------------------------------------

                try:

                    await message.reply_text(
                        text=_text,
                        reply_markup=key,
                        quote=not private,
                    )

                except Exception as final_error:

                    logger.error(
                        f"Final /start failed: "
                        f"{final_error}",
                        exc_info=True
                    )

        else:

            # ------------------------------------------------
            # Final fallback: TEXT + BUTTONS
            # ------------------------------------------------

            try:

                await message.reply_text(
                    text=_text,
                    reply_markup=key,
                    quote=not private,
                )

            except Exception as final_error:

                logger.error(
                    f"Final /start failed: "
                    f"{final_error}",
                    exc_info=True
                )

    # ------------------------------------------------------
    # Save user
    # ------------------------------------------------------

    if private:

        try:

            if await db.is_user(
                message.from_user.id
            ):
                return

            await utils.send_log(message)

            await db.add_user(
                message.from_user.id
            )

        except Exception as db_error:

            logger.error(
                f"User registration error: {db_error}",
                exc_info=True
            )


# ==========================================================
# GROUP SETTINGS
# ==========================================================

@app.on_message(
    filters.command(
        ["playmode", "settings"]
    )
    & filters.group
    & ~app.bl_users
)
@lang.language()
async def settings(_, message: types.Message):
    """Handle group settings."""

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
            message.chat.id
        ),
        quote=True,
    )


# ==========================================================
# NEW GROUP MEMBER / BOT ADDED
# ==========================================================

@app.on_message(
    filters.new_chat_members,
    group=7
)
@lang.language()
async def _new_member(_, message: types.Message):
    """Detect when bot is added to groups."""

    if (
        message.chat.type
        != enums.ChatType.SUPERGROUP
    ):
        return await message.chat.leave()

    for member in message.new_chat_members:

        if member.id == app.id:

            if await db.is_chat(
                message.chat.id
            ):
                return

            await db.add_chat(
                message.chat.id
            )
