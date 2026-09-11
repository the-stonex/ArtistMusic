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

import os
import platform
import sys

import psutil
from pyrogram import __version__, filters, types
from pytgcalls import __version__ as pytgver

from ArtistMusic import app, config, db, lang, userbot
from ArtistMusic.plugins import all_modules


@app.on_message(filters.command(["stats"]) & ~app.bl_users)
@lang.language()
async def _stats(_, m: types.Message):

    # Auto-delete command message
    try:
        await m.delete()
    except Exception:
        pass

    # Check user
    if not m.from_user:
        return

    # Check sudo
    if m.from_user.id not in app.sudoers:
        return

    # Send fetching message
    sent = None

    if config.PING_IMG:
        try:
            sent = await m.reply_photo(
                photo=config.PING_IMG,
                caption=m.lang["stats_fetching"],
            )
        except Exception:
            sent = None

    # If PING_IMG is empty/invalid, use text
    if sent is None:
        sent = await m.reply_text(
            m.lang["stats_fetching"]
        )

    # Process ID
    pid = os.getpid()

    # CPU
    cpu_percent = psutil.cpu_percent(interval=0.5)
    cpu_count = psutil.cpu_count() or 0

    # Memory
    mem = psutil.virtual_memory()
    used_mem = round(
        mem.used / (1024 ** 3),
        2,
    )
    total_mem = round(
        mem.total / (1024 ** 3),
        2,
    )

    # Disk
    disk = psutil.disk_usage("/")
    used_disk = round(
        disk.used / (1024 ** 3),
        2,
    )
    total_disk = round(
        disk.total / (1024 ** 3),
        2,
    )

    # Database stats
    chats = await db.get_chats()
    users = await db.get_users()

    # User stats
    _utext = m.lang["stats_user"].format(
        app.name,
        len(userbot.clients),
        config.AUTO_LEAVE,
        len(db.blacklisted),
        len(app.bl_users),
        len(app.sudoers),
        len(chats),
        len(users),
    )

    # System stats
    _utext += m.lang["stats_sudo"].format(
        len(all_modules),
        platform.system(),
        f"{used_mem}GB | {total_mem}GB",
        f"{cpu_percent}% ({cpu_count} cores)",
        f"{used_disk}GB | {total_disk}GB",
        sys.version.split()[0],
        __version__,
        pytgver,
    )

    # Update final stats message
    try:
        if sent.photo:
            await sent.edit_caption(_utext)
        else:
            await sent.edit_text(_utext)

    except Exception:
        # Final fallback
        try:
            await sent.delete()
        except Exception:
            pass

        await m.reply_text(_utext)
