# Lucida Telegram Bot

A Dockerized Telegram bot that accepts Qobuz/Spotify/Amazon URLs, downloads high-quality lossless music using the `lucida.to` service via a Rust backend, and uploads the files to Telegram.

## Features
- **High-Quality Lossless Music**: Downloads tracks seamlessly via the `lucida.to` service.
- **Dual-Client Upload System**: Bypasses Telegram's 50MB bot limit using a User Client to support files up to 2GB/4GB.
- **Audio Metadata Detection**: Automatically extracts and displays the **Duration** and **Lyrics Availability** for uploaded audio files.
- **Cloudflare Bypass Support**: Per-user proxy and user-agent support to pass WAF protections securely.

## Setup & Deployment

1. Rename `.env.example` to `.env` and fill in the required variables (API keys, Session Strings, Owner ID, etc.).
2. Run via Docker Compose:
   ```bash
   docker-compose up -d
   ```

## Bot Commands
- `/start` - Start interacting with the bot.
- `/setcfcookie` - Set your Cloudflare clearance cookie (reply to the message containing the token).
- `/setuseragent` - Set your User-Agent (reply to the message).
- `/setproxy` - Set a SOCKS5 proxy URL (reply to the message).
- `/adduser <id>` - (Owner) Authorize a user to use the bot.
- `/remuser <id>` - (Owner) Remove authorization for a user.

For more architectural details and the decision log, refer to the [PROJECT_CONTEXT.md](PROJECT_CONTEXT.md).
