# Lucida Telegram Bot - Project Context

**To any future AI Assistant or Developer reading this:**
This file serves as the architectural context and decision log for the `lucida-tg-bot` project. The user created this file so you can immediately understand the project state and pick up exactly where we left off.

## 🎯 Goal
A Dockerized Telegram bot that accepts Qobuz/Spotify/Amazon URLs, downloads high-quality lossless music using the `lucida.to` service via a Rust backend (`lucida-downloader`), and uploads the files to Telegram.

## 🏗️ Architecture & Core Components
- **Framework:** Python 3.11+, using `kurigram` (a `pyrogram` fork) for the Telegram MTProto API.
- **Dual-Client System:** 
  - `bot_client`: A standard Bot API client used for commands, progress messages, and UI.
  - `user_client`: A User String Session client used *exclusively* for uploading the final files. This bypasses Telegram's standard 50MB bot limit and allows for 2GB/4GB file uploads.
- **Rust Backend Wrapper:** Instead of interacting with the Lucida API directly in Python, the bot uses `asyncio.create_subprocess_exec` to call a pre-compiled Rust binary (`lucida-bin`). It reads `stdout` to stream progress percentages back to Telegram.
- **Sequential Queue:** `bot/queue_manager.py` enforces a strict 1-at-a-time global download and upload queue to protect against Cloudflare and Telegram flood bans. Progress messages update every 15 seconds.

## 🔐 Authentication & Cloudflare Bypasses
The biggest hurdle in this project was bypassing Cloudflare's `cf_clearance` IP-binding WAF.
1. **The Issue:** Cloudflare binds the `cf_clearance` cookie to the exact IP address that solved the captcha. If the bot runs on a VPS but the user generates the cookie at home, Cloudflare rejects the cookie due to the IP mismatch.
2. **The Proxy Solution:** The Rust backend (`reqwest`) natively supports `ALL_PROXY`. We implemented a per-user SQLite database. The user connects their home browser to an IPVanish SOCKS5 proxy, generates the cookie, and then sends both the cookie and the `socks5h://...` proxy URL to the bot. The bot isolates that user's subprocess and injects `ALL_PROXY`, perfectly matching the IPs and bypassing Cloudflare.

## 📁 Command Reference
- `/setcfcookie` (Reply to token) - Saves cookie, auto-deletes the message for security.
- `/setuseragent` (Reply to UA) - Saves UA, auto-deletes the message.
- `/setproxy` (Reply to proxy) - Saves proxy URL, auto-deletes the message.
- `/adduser <id>` / `/remuser <id>` - Rewrites the `.env` file dynamically via `python-dotenv`.
- URL Handler - Triggers the download queue and uploads the track as a **raw Document**.

## 🚀 Deployment
Deployed via `docker-compose up -d`. Mounts `.env` and `/data` (for `users.db` and session files).
