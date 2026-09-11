<div align="center">  <img src="https://files.catbox.moe/f4nnyn.svg" width="100%" height="500">  <br>  
<br><br>  




<br>  


</div>  <br>  <div align="center">  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  
                   ✦  ARTISTMUSIC MUSIC BOT  ✦  
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

</div>  📖 Table of Contents

Overview

Feature Showcase

Requirements

Environment Variables

Deploy

Commands

Security

Support

Credits


<br>  〔 ✦ 〕 Overview

> ArtistMusic is a next-generation Telegram Voice Chat Music Bot engineered for performance, stability, and scale.
Built on Pyrogram · PyTgCalls · MongoDB — delivering crystal-clear audio with powerful admin tooling and multi-language support across global communities.



<br>  〔 ✦ 〕 Feature Showcase

<table>  
<tr>  
<td width="50%">  🎵 Music Streaming

✦ High Quality Audio Streaming  
✦ YouTube Search & Play  
✦ Direct URL Playback  
✦ Voice Chat Streaming  
✦ Live Stream Support  
✦ Playlist Management  
✦ Auto Queue System  
✦ Continuous Playback  
✦ Fast Audio Processing

</td>  
<td width="50%">  🎛 Admin Controls

✦ Pause / Resume Stream  
✦ Skip Current Track  
✦ Force Play (Skip Queue)  
✦ Stop Playback  
✦ Mute / Unmute Assistant  
✦ Volume Control  
✦ Queue Cleanup  
✦ Seek Forward / Backward  
✦ Loop Modes

</td>  
</tr>  
<tr>  
<td width="50%">  👥 User Management

✦ Authorized Users System  
✦ Sudo Users Panel  
✦ Global Ban System  
✦ User Statistics  
✦ Blacklist Chat / User  
✦ Owner Controls  
✦ Admin-Only Play Mode  
✦ Force Admin Mode

</td>  
<td width="50%">  🤖 Bot Management

✦ Restart Command  
✦ Broadcast System  
✦ Maintenance Mode  
✦ Live Logs Monitor  
✦ Error Reporting  
✦ Auto Restart Support  
✦ MongoDB Integration  
✦ Multi-Language Support

</td>  
</tr>  
</table>  <br>  〔 ✦ 〕 Requirements

Component	Minimum Version / Note

Python	3.10 or higher
FFmpeg	Latest stable release
MongoDB	Local instance or Atlas cluster
RAM	512 MB minimum (1 GB+ recommended)
Telegram Account	For the assistant (string session)


<br>  〔 ✦ 〕 Environment Variables

<div align="center">  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  
         Create a  .env  file with these values  
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

</div>  Variable	Required	Description

API_ID	✅	Telegram API ID — my.telegram.org
API_HASH	✅	Telegram API Hash — my.telegram.org
BOT_TOKEN	✅	Bot Token — @BotFather
STRING_SESSION	✅	Pyrogram String Session for assistant
MONGO_DB_URI	✅	MongoDB connection string
LOGGER_ID	✅	Telegram group ID for logs
OWNER_ID	✅	Your Telegram user ID
ARTISTBOTS_API_URL	⚙️	ArtistBots API endpoint
ARTISTBOTS_KEY	⚙️	API key — @ArtistApibot
SUPPORT_CHAT	🔵	Support group link (optional)
SUPPORT_CHANNEL	🔵	Updates channel link (optional)
START_IMG	🔵	Start message image URL (optional)
PING_IMG	🔵	Ping message image URL (optional)
STRING_SESSION2	🔵	Second assistant session (optional)
STRING_SESSION3	🔵	Third assistant session (optional)


> ✅ Required · ⚙️ Recommended · 🔵 Optional



<br>  〔 ✦ 〕 Deploy

<div align="center">  ☁️ One-Click Deploy




</div>  <br>  <details>  
<summary><b>🖥 Render — Step by Step</b></summary>  <br>  1. Fork this repository

2. Go to render.com → New Web Service

3. Connect your GitHub and select this repo

4. Set build & start commands:

# Build Command  
pip install -U -r requirements.txt  
  
# Start Command  
bash start

5. Add all environment variables from the table above

6. Hit Deploy 🚀

</details>  <details>  
<summary><b>🚂 Railway — Step by Step</b></summary>  <br>  1. Fork this repository

2. Create a new project at railway.app

3. Connect your GitHub repo

4. Add environment variables

5. Deploy 🚀

</details>  <details>  
<summary><b>🖥 VPS / Self-Host</b></summary>  <br>  # Update system  
apt update && apt upgrade -y  
  
# Install dependencies  
apt install python3 python3-pip ffmpeg git -y  
  
# Clone repo  
git clone https://github.com/elevenyts/ArtistMusic  
cd ArtistMusic  
  
# Install requirements  
pip3 install -U -r requirements.txt  
  
# Configure variables  
cp .env.example .env  
nano .env  
  
# Run the bot  
bash start  
# or  
python -m ArtistMusic

</details>  <details>  
<summary><b>🐳 Docker</b></summary>  <br>  # Build the image  
docker build -t artistmusic .  
  
# Run the container (pass your .env file)  
docker run -d --env-file .env --name artistmusic artistmusic

</details>  <br>  〔 ✦ 〕 Commands

<table>  
<tr>  
<td width="33%">  🎵 Music

/play    — Play audio  
/vplay   — Play video  
/cplay   — Channel play  
/pause   — Pause stream  
/resume  — Resume stream  
/skip    — Skip track  
/end     — End stream  
/queue   — View queue  
/loop    — Loop mode  
/shuffle — Shuffle queue

</td>  
<td width="33%">  🛡 Admin

/reload   — Refresh admins  
/auth     — Authorize user  
/unauth   — Remove auth  
/authlist — View auth list  
/seek     — Seek stream  
/seekback — Seek backward  
/mute     — Mute assistant  
/unmute   — Unmute assistant  
/volume   — Set volume  
/stop     — Stop playback

</td>  
<td width="33%">  👑 Sudo / Owner

/addsudo     — Add sudo user  
/delsudo     — Remove sudo  
/sudolist    — List sudos  
/broadcast   — Send broadcast  
/gban        — Global ban  
/ungban      — Global unban  
/maintenance — Toggle mode  
/stats       — Bot statistics  
/restart     — Restart bot  
/logs        — View logs

</td>  
</tr>  
</table>  <br>  〔 ✦ 〕 Security

<div align="center">  ╔══════════════════════════════════════════════════════╗  
║  ✦  KEEP THESE PRIVATE — NEVER SHARE PUBLICLY  ✦    ║  
╠══════════════════════════════════════════════════════╣  
║  ✗  BOT_TOKEN          ✗  STRING_SESSION             ║  
║  ✗  MONGO_DB_URI       ✗  API_HASH                   ║  
║  ✓  Use a separate Telegram account for assistant    ║  
║  ✓  Keep the logger group private                    ║  
║  ✓  Bot must be admin in group & logger group        ║  
╚══════════════════════════════════════════════════════╝

</div>  <br>  〔 ✦ 〕 Support

<div align="center">  Facing an issue? Send a screenshot to our support group.

<br>  

<br>  Platform	Link

📢 Updates Channel	t.me/Artistbots
💬 Support Group	t.me/artistmusicmusic


</div>  <br>  〔 ✦ 〕 Credits

<div align="center">  Built on the shoulders of giants:

Pyrogram · PyTgCalls · MongoDB · Telegram Bot API · ArtistBots

<br>  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  
         Made with ❤️  by  Artist  ·  Powered by ArtistBots  
                   © 2026 ArtistMusic · MIT License  
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

</div>  Isme kuch change nahi Krna bs meri heroku deploy button or add Krna jha tendar or railway h usi k pass
Pura baki same
