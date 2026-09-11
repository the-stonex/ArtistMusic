from pyrogram import enums, filters, types

from ArtistMusic import app, config, db, lang
from ArtistMusic.helpers import buttons, utils


@app.on_message(filters.command(["help"]) & filters.private & ~app.bl_users)
@lang.language()
async def _help(_, m: types.Message):

    try:
        await m.delete()
    except Exception:
        pass

    text = m.lang["help_menu"]
    markup = buttons.help_markup(m.lang)

    if config.START_IMG:
        try:
            return await m.reply_photo(
                photo=config.START_IMG,
                caption=text,
                reply_markup=markup,
                quote=True,
            )
        except Exception:
            pass

    await m.reply_text(
        text=text,
        reply_markup=markup,
        quote=True,
    )


@app.on_message(filters.command(["start"]))
@lang.language()
async def start(_, message: types.Message):

    if message.chat.type != enums.ChatType.PRIVATE:
        try:
            await message.delete()
        except Exception:
            pass

    if not message.from_user:
        return

    if (
        message.from_user.id in app.bl_users
        and message.from_user.id not in db.notified
    ):
        return await message.reply_text(
            message.lang["bl_user_notify"]
        )

    if len(message.command) > 1 and message.command[1] == "help":
        return await _help(_, message)

    private = message.chat.type == enums.ChatType.PRIVATE

    if private:
        text = message.lang["start_pm"].format(
            message.from_user.first_name,
            app.name,
        )
    else:
        text = message.lang["start_gp"].format(app.name)

    # Existing language/channel/developer/etc buttons
    markup = buttons.start_key(message.lang, private)

    # Send start image if available
    if config.START_IMG:
        try:
            await message.reply_photo(
                photo=config.START_IMG,
                caption=text,
                reply_markup=markup,
                quote=not private,
            )
        except Exception:
            try:
                await message.reply_text(
                    text=text,
                    reply_markup=markup,
                    quote=not private,
                )
            except Exception:
                pass
    else:
        # START_IMG empty → text + same buttons
        try:
            await message.reply_text(
                text=text,
                reply_markup=markup,
                quote=not private,
            )
        except Exception:
            pass

    # Save private users
    if private:
        if await db.is_user(message.from_user.id):
            return

        try:
            await utils.send_log(message)
        except Exception:
            pass

        await db.add_user(message.from_user.id)


@app.on_message(
    filters.command(["playmode", "settings"])
    & filters.group
    & ~app.bl_users
)
@lang.language()
async def settings(_, message: types.Message):

    try:
        await message.delete()
    except Exception:
        pass

    admin_only = await db.get_play_mode(message.chat.id)
    force_admin = await db.get_force_mode(message.chat.id)

    await utils.safe_text(
        message,
        message.lang["start_settings"].format(
            message.chat.title
        ),
        reply_markup=buttons.settings_markup(
            message.lang,
            admin_only,
            force_admin,
            "en",
            message.chat.id,
        ),
        quote=True,
    )


@app.on_message(filters.new_chat_members, group=7)
@lang.language()
async def _new_member(_, message: types.Message):

    if message.chat.type != enums.ChatType.SUPERGROUP:
        return await message.chat.leave()

    for member in message.new_chat_members:

        if member.id == app.id:

            if await db.is_chat(message.chat.id):
                return

            await db.add_chat(message.chat.id)
