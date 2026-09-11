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
import re
import glob
import time
import yt_dlp
import random
import asyncio
import aiohttp

from dataclasses import replace
from pathlib import Path
from typing import Optional, Union

from pyrogram import enums, types
from py_yt import Playlist, VideosSearch

from ArtistMusic import config, logger
from ArtistMusic.helpers import Track, utils


class YouTube:
    def __init__(self):
        """Initialize YouTube handler with configuration and caching."""

        self.base = "https://www.youtube.com/watch?v="

        self.cookies = []
        self.checked = False
        self.warned = False

        # ==================================================
        # Shruti API Configuration
        # ==================================================

        self.api_url = config.SHRUTI_API_URL
        self.shruti_key = config.SHRUTI_API_KEY

        self.enable_api = config.ENABLE_API
        self.enable_cookies_fallback = config.ENABLE_COOKIES_FALLBACK

        self.api_timeout = config.API_TIMEOUT
        self.api_stream_timeout = config.API_STREAM_TIMEOUT

        # ==================================================
        # YouTube URL Regex
        # ==================================================

        self.regex = re.compile(
            r"(https?://)?(www\.|m\.|music\.)?"
            r"(youtube\.com/(watch\?v=|shorts/|live/|embed/|playlist\?list=)|youtu\.be/)"
            r"([A-Za-z0-9_-]{11}|PL[A-Za-z0-9_-]+)([&?][^\s]*)?"
        )

        # ==================================================
        # Search Cache
        # ==================================================

        self.search_cache = {}

        self._download_semaphore = asyncio.Semaphore(5)

        self._max_video_height = config.VIDEO_MAX_HEIGHT

        # ==================================================
        # Logging
        # ==================================================

        logger.info("=" * 50)
        logger.info("📹 YouTube Handler Initialized")

        logger.info(
            f"🎵 API Priority: "
            f"{'ENABLED' if self.enable_api else 'DISABLED'}"
        )

        if self.enable_api:

            logger.info(
                f"🔗 API URL: {self.api_url}"
            )

            if self.shruti_key:

                masked_key = (
                    self.shruti_key[:8] + "..."
                    if len(self.shruti_key) > 8
                    else "***"
                )

                logger.info(
                    f"🔑 Shruti API Key: {masked_key}"
                )

            else:

                logger.warning(
                    "⚠️ SHRUTI_API_KEY is not configured!"
                )

        logger.info(
            f"🍪 Cookies Fallback: "
            f"{'ENABLED' if self.enable_cookies_fallback else 'DISABLED'}"
        )

        logger.info("=" * 50)

    # ======================================================
    # Locate Downloaded File
    # ======================================================

    def _locate_download_file(
        self,
        video_id: str,
        video: bool = False
    ) -> Optional[str]:

        """Locate any completed download file for a video id."""

        pattern = f"downloads/{video_id}*"

        candidates = sorted([
            path
            for path in glob.glob(pattern)
            if not path.endswith(
                (
                    ".part",
                    ".ytdl",
                    ".info.json",
                    ".temp"
                )
            )
        ])

        video_exts = {
            ".mp4",
            ".mkv",
            ".webm",
            ".mov"
        }

        audio_exts = {
            ".m4a",
            ".webm",
            ".opus",
            ".mp3",
            ".ogg",
            ".wav",
            ".flac"
        }

        if video:

            for path in candidates:

                if os.path.isdir(path):
                    continue

                if Path(path).suffix.lower() in video_exts:
                    return path

        else:

            for path in candidates:

                if os.path.isdir(path):
                    continue

                if Path(path).suffix.lower() in audio_exts:
                    return path

        for path in candidates:

            if os.path.isdir(path):
                continue

            return path

        return None

    # ======================================================
    # Cookies
    # ======================================================

    def get_cookies(self):

        """Get random cookie file from cookies directory."""

        if not self.checked:

            cookies_dir = "ArtistMusic/cookies"

            if os.path.exists(cookies_dir):

                for file in os.listdir(cookies_dir):

                    if file.endswith(".txt"):
                        self.cookies.append(file)

            self.checked = True

        if not self.cookies:

            if not self.warned:

                self.warned = True

                logger.warning(
                    "🍪 Cookies are missing; downloads might fail."
                )

            return None

        cookie_file = (
            f"ArtistMusic/cookies/"
            f"{random.choice(self.cookies)}"
        )

        logger.debug(
            f"Using cookie file: {cookie_file}"
        )

        return cookie_file

    # ======================================================
    # Save Cookies
    # ======================================================

    async def save_cookies(
        self,
        urls: list[str]
    ) -> None:

        """Save cookies from URLs to files."""

        logger.info("🍪 Saving cookies from urls...")

        saved_count = 0

        cookies_dir = Path(
            "ArtistMusic/cookies"
        )

        cookies_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        for url in urls:

            try:

                path = cookies_dir / (
                    f"cookie{random.randint(10000, 99999)}.txt"
                )

                if "pastebin.com" in url:

                    link = url.replace(
                        "pastebin.com",
                        "pastebin.com/raw"
                    )

                elif "batbin.me" in url:

                    link = url.replace(
                        "batbin.me",
                        "batbin.me/raw"
                    )

                else:

                    link = url

                async with aiohttp.ClientSession() as session:

                    async with session.get(
                        link,
                        timeout=aiohttp.ClientTimeout(
                            total=30
                        )
                    ) as resp:

                        if resp.status != 200:

                            logger.error(
                                f"❌ Cookie download failed: "
                                f"HTTP {resp.status} from {url}"
                            )

                            continue

                        content = await resp.read()

                        if not content or len(content) < 50:

                            logger.error(
                                f"❌ Cookie file empty or invalid from {url}"
                            )

                            continue

                        with open(
                            path,
                            "wb"
                        ) as fw:

                            fw.write(content)

                        if (
                            path.exists()
                            and path.stat().st_size > 0
                        ):

                            saved_count += 1

                            cookie_filename = path.name

                            if cookie_filename not in self.cookies:

                                self.cookies.append(
                                    cookie_filename
                                )

                            logger.info(
                                f"✅ Saved: "
                                f"{cookie_filename} "
                                f"({len(content)} bytes)"
                            )

            except asyncio.TimeoutError:

                logger.error(
                    f"❌ Cookie download timeout from {url}"
                )

            except Exception as e:

                logger.error(
                    f"❌ Cookie download error "
                    f"from {url}: {e}"
                )

        self.checked = True

        if saved_count > 0:

            logger.info(
                f"✅ Cookies saved successfully! "
                f"({saved_count} file(s))"
            )

        else:

            logger.error(
                "❌ No cookies saved! "
                "Check COOKIE_URL in .env."
            )

    # ======================================================
    # Shruti API Download
    # ======================================================

    async def download_via_api(
        self,
        link: str,
        video: bool = False
    ) -> Optional[str]:

        """
        Download audio/video using Shruti API.

        API:
        https://api01.shrutibots.site/download
        """

        if not self.enable_api:

            logger.debug(
                "API is disabled in config"
            )

            return None

        if not self.api_url:

            logger.error(
                "SHRUTI_API_URL is not configured"
            )

            return None

        if not self.shruti_key:

            logger.error(
                "SHRUTI_API_KEY is not configured"
            )

            return None

        # ==================================================
        # Extract YouTube Video ID
        # ==================================================

        try:

            if "v=" in link:

                video_id = (
                    link.split("v=", 1)[1]
                    .split("&", 1)[0]
                )

            elif "youtu.be/" in link:

                video_id = (
                    link.split("youtu.be/", 1)[1]
                    .split("?", 1)[0]
                )

            elif "/shorts/" in link:

                video_id = (
                    link.split("/shorts/", 1)[1]
                    .split("?", 1)[0]
                )

            elif "/live/" in link:

                video_id = (
                    link.split("/live/", 1)[1]
                    .split("?", 1)[0]
                )

            else:

                video_id = link.strip()

        except Exception as e:

            logger.error(
                f"❌ Failed to extract video ID: {e}"
            )

            return None

        if not video_id or len(video_id) < 3:

            logger.error(
                f"❌ Invalid video ID: {video_id}"
            )

            return None

        # ==================================================
        # File Setup
        # ==================================================

        download_dir = Path("downloads")

        download_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        download_type = (
            "video"
            if video
            else "audio"
        )

        file_ext = (
            ".mp4"
            if video
            else ".mp3"
        )

        file_path = (
            download_dir
            / f"{video_id}{file_ext}"
        )

        # Existing file

        if (
            file_path.exists()
            and file_path.stat().st_size > 0
        ):

            logger.info(
                f"📁 Existing file found: {file_path}"
            )

            return str(file_path)

        # ==================================================
        # API Parameters
        # ==================================================

        params = {
            "url": video_id,
            "type": download_type,
            "api_key": self.shruti_key,
        }

        timeout = (
            600
            if video
            else 300
        )

        try:

            logger.info(
                f"🚀 [SHRUTI API] "
                f"Downloading {download_type}: "
                f"{video_id}"
            )

            endpoint = (
                f"{self.api_url.rstrip('/')}"
                f"/download"
            )

            async with aiohttp.ClientSession() as session:

                async with session.get(
                    endpoint,
                    params=params,
                    timeout=aiohttp.ClientTimeout(
                        total=timeout
                    )
                ) as response:

                    logger.info(
                        f"📡 Shruti API response: "
                        f"HTTP {response.status}"
                    )

                    if response.status != 200:

                        try:

                            error_text = (
                                await response.text()
                            )

                            logger.error(
                                f"❌ Shruti API error "
                                f"{response.status}: "
                                f"{error_text[:300]}"
                            )

                        except Exception:

                            logger.error(
                                f"❌ Shruti API returned "
                                f"HTTP {response.status}"
                            )

                        return None

                    downloaded = 0
                    last_log = 0

                    # ======================================
                    # Stream API Response To File
                    # ======================================

                    with open(
                        file_path,
                        "wb"
                    ) as f:

                        async for chunk in (
                            response.content.iter_chunked(
                                131072
                            )
                        ):

                            if not chunk:
                                continue

                            f.write(chunk)

                            downloaded += len(chunk)

                            # Log every 5 MB

                            if (
                                downloaded - last_log
                                >= 5 * 1024 * 1024
                            ):

                                size_mb = (
                                    downloaded
                                    / (1024 * 1024)
                                )

                                logger.info(
                                    f"📥 Downloaded "
                                    f"{size_mb:.1f} MB"
                                )

                                last_log = downloaded

            # ==================================================
            # Verify File
            # ==================================================

            if (
                file_path.exists()
                and file_path.stat().st_size > 0
            ):

                size_mb = (
                    file_path.stat().st_size
                    / (1024 * 1024)
                )

                logger.info(
                    f"✅ [SHRUTI API SUCCESS] "
                    f"{file_path} "
                    f"({size_mb:.2f} MB)"
                )

                return str(file_path)

            logger.error(
                "❌ Shruti API returned an empty file"
            )

        except asyncio.TimeoutError:

            logger.error(
                f"⏰ Shruti API timeout "
                f"for {video_id}"
            )

        except aiohttp.ClientError as e:

            logger.error(
                f"🌐 Shruti API connection error: {e}"
            )

        except Exception as e:

            logger.error(
                f"❌ Shruti API download failed "
                f"for {video_id}: "
                f"{type(e).__name__}: {e}"
            )

        # Remove incomplete file

        try:

            if file_path.exists():
                file_path.unlink()

        except Exception:
            pass

        return None

    # ======================================================
    # Cookies Download
    # ======================================================

    async def download_via_cookies(
        self,
        video_id: str,
        video: bool = False
    ) -> Optional[str]:

        """
        Download audio/video using yt-dlp
        with cookies as fallback.
        """

        if not self.enable_cookies_fallback:

            logger.debug(
                "Cookies fallback is disabled in config"
            )

            return None

        url = self.base + video_id

        filename_pattern = (
            f"downloads/{video_id}"
        )

        existing_files = [
            f
            for f in glob.glob(
                f"{filename_pattern}.*"
            )
            if not f.endswith(".part")
        ]

        if video:

            video_candidates = [
                f
                for f in existing_files
                if Path(f).suffix.lower()
                in {
                    ".mp4",
                    ".mkv",
                    ".webm",
                    ".mov"
                }
            ]

            if video_candidates:

                logger.debug(
                    f"Found existing video file: "
                    f"{video_candidates[0]}"
                )

                return video_candidates[0]

        else:

            audio_candidates = [
                f
                for f in existing_files
                if Path(f).suffix.lower()
                in {
                    ".m4a",
                    ".webm",
                    ".opus",
                    ".mp3",
                    ".ogg",
                    ".wav",
                    ".flac"
                }
            ]

            if audio_candidates:

                logger.debug(
                    f"Found existing audio file: "
                    f"{audio_candidates[0]}"
                )

                return audio_candidates[0]

            container_fallbacks = [
                f
                for f in existing_files
                if Path(f).suffix.lower()
                in {
                    ".mp4",
                    ".mkv",
                    ".mov"
                }
            ]

            if container_fallbacks:

                logger.debug(
                    f"Found existing container file: "
                    f"{container_fallbacks[0]}"
                )

                return container_fallbacks[0]

        # ==================================================
        # Downloads Directory
        # ==================================================

        downloads_dir = Path("downloads")

        if not downloads_dir.exists():

            try:

                downloads_dir.mkdir(
                    parents=True,
                    exist_ok=True
                )

                logger.info(
                    "📁 Created downloads directory"
                )

            except Exception as e:

                logger.error(
                    f"❌ Cannot create downloads directory: {e}"
                )

                return None

        # ==================================================
        # Download Semaphore
        # ==================================================

        async with self._download_semaphore:

            cookie = self.get_cookies()

            base_opts = {

                "outtmpl":
                    "downloads/%(id)s.%(ext)s",

                "quiet": True,

                "noplaylist": True,

                "geo_bypass": True,

                "no_warnings": True,

                "overwrites": False,

                "nocheckcertificate": True,

                "continuedl": True,

                "noprogress": True,

                "concurrent_fragment_downloads": 4,

                "http_chunk_size": 524288,

                "socket_timeout": 30,

                "retries": 2,

                "fragment_retries": 2,

                "extractor_retries": 5,

                "sleep_interval_requests": 1,

                "extractor_args": {
                    "youtube": {
                        "player_client": [
                            "android",
                            "web"
                        ]
                    }
                },
            }

            # ==================================================
            # Video Options
            # ==================================================

            if video:

                height_filter = ""

                if (
                    self._max_video_height
                    and self._max_video_height > 0
                ):

                    height_filter = (
                        f"[height<="
                        f"{self._max_video_height}]"
                    )

                format_chain = (

                    f"bestvideo[ext=mp4]"
                    f"{height_filter}+"
                    f"bestaudio[ext=m4a]/"

                    f"bestvideo"
                    f"{height_filter}+"
                    f"bestaudio/"

                    "bestvideo+bestaudio/"
                    "best"
                )

                ydl_opts = {

                    **base_opts,

                    "format": format_chain,

                    "merge_output_format": "mp4",

                    "postprocessors": [
                        {
                            "key":
                                "FFmpegVideoConvertor",

                            "preferedformat":
                                "mp4",
                        }
                    ],
                }

            else:

                ydl_opts = {

                    **base_opts,

                    "format":
                        "bestaudio[ext=m4a]/"
                        "bestaudio[acodec=opus]/"
                        "bestaudio/best",

                    "postprocessors": [],
                }

            ydl_opts_cookie = {

                **ydl_opts,

                "cookiefile": cookie,
            }

            # ==================================================
            # yt-dlp Worker
            # ==================================================

            def _download(
                ydl_runtime_opts
            ):

                ydl_instance = None

                try:

                    ydl_instance = yt_dlp.YoutubeDL(
                        ydl_runtime_opts
                    )

                    info = ydl_instance.extract_info(
                        url,
                        download=True
                    )

                    if not info:

                        logger.error(
                            f"❌ Failed to extract info "
                            f"for {video_id}"
                        )

                        return None

                    time.sleep(0.5)

                    located = (
                        self._locate_download_file(
                            video_id,
                            video=video
                        )
                    )

                    if located:

                        logger.info(
                            f"✅ Download completed: "
                            f"{located}"
                        )

                        return located

                    logger.error(
                        f"❌ Download completed but "
                        f"file not found for: {video_id}"
                    )

                    return None

                except Exception as ex:

                    logger.warning(
                        f"⚠️ Download error for "
                        f"{video_id}: {ex}"
                    )

                    recovered = (
                        self._locate_download_file(
                            video_id,
                            video=video
                        )
                    )

                    if recovered:

                        logger.info(
                            f"✅ Recovered existing file: "
                            f"{recovered}"
                        )

                        return recovered

                    return None

                finally:

                    if ydl_instance:

                        try:
                            ydl_instance.close()

                        except Exception:
                            pass

            logger.info(
                f"🍪 [COOKIES FALLBACK] "
                f"Downloading {video_id} "
                f"with cookies..."
            )

            result = await asyncio.to_thread(
                _download,
                ydl_opts_cookie
            )

            if result:

                logger.info(
                    f"✅ [COOKIES SUCCESS] "
                    f"Downloaded: {result}"
                )

            else:

                logger.warning(
                    f"⚠️ [COOKIES FAILED] "
                    f"Could not download {video_id}"
                )

            return result

    # ======================================================
    # Validate URL
    # ======================================================

    def valid(
        self,
        url: str
    ) -> bool:

        """Check if URL is a valid YouTube URL."""

        return bool(
            re.match(
                self.regex,
                url
            )
        )

    # ======================================================
    # Extract URL
    # ======================================================

    def url(
        self,
        message_1: types.Message
    ) -> Union[str, None]:

        """Extract YouTube URL from message."""

        messages = [message_1]

        link = None

        if message_1.reply_to_message:

            messages.append(
                message_1.reply_to_message
            )

        for message in messages:

            text = (
                message.text
                or message.caption
                or ""
            )

            if message.entities:

                for entity in message.entities:

                    if (
                        entity.type
                        == enums.MessageEntityType.URL
                    ):

                        link = text[
                            entity.offset:
                            entity.offset + entity.length
                        ]

                        break

            if message.caption_entities:

                for entity in message.caption_entities:

                    if (
                        entity.type
                        == enums.MessageEntityType.TEXT_LINK
                    ):

                        link = entity.url

                        break

        if link:

            return (
                link
                .split("&si")[0]
                .split("?si")[0]
            )

        return None

    # ======================================================
    # Search
    # ======================================================

    async def search(
        self,
        query: str,
        m_id: int
    ) -> Track | None:

        """Search for a song on YouTube."""

        cache_key = query

        current_time = (
            asyncio.get_running_loop().time()
        )

        if cache_key in self.search_cache:

            cached_result, cache_timestamp = (
                self.search_cache[cache_key]
            )

            if (
                current_time
                - cache_timestamp
                < 600
            ):

                fresh = replace(
                    cached_result
                )

                fresh.message_id = m_id
                fresh.file_path = None
                fresh.user = None
                fresh.time = 0
                fresh.video = False

                return fresh

        try:

            _search = VideosSearch(
                query,
                limit=1
            )

            results = await _search.next()

        except Exception as e:

            logger.warning(
                f"⚠️ YouTube search failed "
                f"for '{query}': {e}"
            )

            return None

        if results and results["result"]:

            data = results["result"][0]

            duration = data.get(
                "duration"
            )

            is_live = (
                duration is None
                or duration == "LIVE"
            )

            track = Track(

                id=data.get("id"),

                channel_name=data.get(
                    "channel",
                    {}
                ).get("name"),

                duration=(
                    duration
                    if not is_live
                    else "LIVE"
                ),

                duration_sec=(
                    0
                    if is_live
                    else utils.to_seconds(
                        duration
                    )
                ),

                message_id=m_id,

                title=data.get(
                    "title"
                )[:25],

                thumbnail=data.get(
                    "thumbnails",
                    [{}]
                )[-1].get(
                    "url"
                ).split("?")[0],

                url=data.get(
                    "link"
                ),

                view_count=data.get(
                    "viewCount",
                    {}
                ).get(
                    "short"
                ),

                is_live=is_live,
            )

            self.search_cache[
                cache_key
            ] = (
                track,
                current_time
            )

            if len(
                self.search_cache
            ) > 100:

                oldest_key = min(
                    self.search_cache.keys(),
                    key=lambda k:
                        self.search_cache[k][1]
                )

                del self.search_cache[
                    oldest_key
                ]

            return replace(track)

        return None

    # ======================================================
    # Playlist
    # ======================================================

    async def playlist(
        self,
        limit: int,
        user: str,
        url: str
    ) -> list[Track]:

        """Extract tracks from a YouTube playlist."""

        try:

            plist = await Playlist.get(
                url
            )

            tracks = []

            if (
                not plist
                or "videos" not in plist
                or not plist["videos"]
            ):

                return []

            for data in plist["videos"][:limit]:

                try:

                    thumbnails = data.get(
                        "thumbnails",
                        []
                    )

                    thumbnail_url = ""

                    if thumbnails:

                        thumbnail_url = (
                            thumbnails[-1]
                            .get("url", "")
                            .split("?")[0]
                        )

                    link = data.get(
                        "link",
                        ""
                    )

                    if "&list=" in link:

                        link = link.split(
                            "&list="
                        )[0]

                    track = Track(

                        id=data.get(
                            "id",
                            ""
                        ),

                        channel_name=data.get(
                            "channel",
                            {}
                        ).get(
                            "name",
                            ""
                        ),

                        duration=data.get(
                            "duration",
                            "0:00"
                        ),

                        duration_sec=utils.to_seconds(
                            data.get(
                                "duration",
                                "0:00"
                            )
                        ),

                        title=data.get(
                            "title",
                            "Unknown"
                        )[:25],

                        thumbnail=thumbnail_url,

                        url=link,

                        user=user,

                        view_count="",
                    )

                    tracks.append(
                        track
                    )

                except Exception as e:

                    logger.warning(
                        f"Failed to parse "
                        f"playlist item: {e}"
                    )

                    continue

            return tracks

        except KeyError:

            raise Exception(
                "Failed to parse playlist. "
                "YouTube may have changed their structure."
            )

        except Exception as e:

            logger.error(
                f"Playlist extraction error: {e}"
            )

            raise

    # ======================================================
    # Main Download
    # ======================================================

    async def download(
        self,
        video_id: str,
        is_live: bool = False,
        video: bool = False
    ) -> Optional[str]:

        """
        Download audio/video from YouTube.

        PRIORITY:
        Shruti API → Cookies Fallback
        """

        # ==================================================
        # Live Stream
        # ==================================================

        if is_live:

            logger.info(
                f"🔴 Live stream detected "
                f"for {video_id}, "
                f"using cookies method..."
            )

            cookie = self.get_cookies()

            ydl_opts = {

                "quiet": True,

                "no_warnings": True,

                "cookiefile": cookie,

                "format":
                    "bestaudio/best",

                "noplaylist": True,

                "socket_timeout": 20,

                "extractor_retries": 5,

                "sleep_interval_requests": 1,

                "extractor_args": {
                    "youtube": {
                        "player_client": [
                            "android",
                            "web"
                        ]
                    }
                },
            }

            def _extract_url():

                with yt_dlp.YoutubeDL(
                    ydl_opts
                ) as ydl:

                    try:

                        info = ydl.extract_info(
                            self.base + video_id,
                            download=False
                        )

                        if not info:
                            return None

                        direct = info.get(
                            "url"
                        )

                        if direct:
                            return direct

                        for fmt in info.get(
                            "formats",
                            []
                        ):

                            if (
                                fmt.get("acodec")
                                != "none"
                                and fmt.get("url")
                            ):

                                return fmt["url"]

                        return info.get(
                            "manifest_url"
                        )

                    except Exception as ex:

                        logger.error(
                            f"Live stream extraction "
                            f"failed: {ex}"
                        )

                        return None

            try:

                stream_url = await asyncio.wait_for(
                    asyncio.to_thread(
                        _extract_url
                    ),
                    timeout=35
                )

                if stream_url:

                    logger.info(
                        f"✅ Live stream URL "
                        f"extracted for {video_id}"
                    )

                return stream_url

            except asyncio.TimeoutError:

                logger.error(
                    f"Live stream URL extraction "
                    f"timed out for {video_id}"
                )

                return None

        # ==================================================
        # Normal Download
        # Shruti API First
        # ==================================================

        result = None

        if (
            self.enable_api
            and self.api_url
            and self.shruti_key
        ):

            logger.info(
                f"🎯 [PRIORITY 1] "
                f"Trying Shruti API "
                f"for {video_id}"
            )

            result = await self.download_via_api(
                self.base + video_id,
                video=video
            )

            if result:

                logger.info(
                    f"✅ [SUCCESS] "
                    f"Downloaded via Shruti API: "
                    f"{video_id}"
                )

                return result

            logger.warning(
                f"⚠️ [SHRUTI API FAILED] "
                f"{video_id}, "
                f"trying cookies fallback..."
            )

        # ==================================================
        # Cookies Fallback
        # ==================================================

        if self.enable_cookies_fallback:

            logger.info(
                f"🍪 [PRIORITY 2] "
                f"Trying cookies download "
                f"for {video_id}"
            )

            result = await self.download_via_cookies(
                video_id,
                video=video
            )

            if result:

                logger.info(
                    f"✅ [SUCCESS] "
                    f"Downloaded via cookies: "
                    f"{video_id}"
                )

                return result

            logger.error(
                f"❌ [COOKIES FAILED] "
                f"Could not download {video_id}"
            )

        # ==================================================
        # All Methods Failed
        # ==================================================

        if not result:

            logger.error(
                f"❌ [FAILED] "
                f"All download methods failed "
                f"for {video_id}"
            )

        return result


YouTube = YouTube()
