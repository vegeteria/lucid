from pyrogram import Client, filters
from bot import config, database, queue_manager

def auth_filter(_, __, message):
    if not message.from_user: return False
    return message.from_user.id in config.get_authorized_users()

is_auth = filters.create(auth_filter)

def owner_filter(_, __, message):
    if not message.from_user: return False
    return message.from_user.id == config.OWNER_ID

is_owner = filters.create(owner_filter)

def register_handlers(app: Client):
    @app.on_message(filters.command("start") & is_auth)
    async def start_cmd(client, message):
        await message.reply_text("👋 Welcome to the Lucida Bot!\nSend me a Qobuz/Spotify/Amazon link to download.")

    @app.on_message(filters.command("adduser") & is_owner)
    async def add_user(client, message):
        try:
            uid = int(message.command[1])
            config.add_authorized_user(uid)
            await message.reply_text(f"✅ Added {uid} to authorized users.")
        except Exception:
            await message.reply_text("Usage: /adduser <telegram_id>")

    @app.on_message(filters.command("remuser") & is_owner)
    async def rem_user(client, message):
        try:
            uid = int(message.command[1])
            config.remove_authorized_user(uid)
            await message.reply_text(f"✅ Removed {uid} from authorized users.")
        except Exception:
            await message.reply_text("Usage: /remuser <telegram_id>")

    @app.on_message(filters.command("setcfcookie") & is_auth & filters.reply)
    async def set_cf(client, message):
        cookie = message.reply_to_message.text.strip()
        await database.update_user_setting(message.from_user.id, "cf_clearance", cookie)
        await message.reply_to_message.delete()
        await message.reply_text("✅ Saved cf_clearance and securely deleted your original message.")

    @app.on_message(filters.command("setuseragent") & is_auth & filters.reply)
    async def set_ua(client, message):
        ua = message.reply_to_message.text.strip()
        await database.update_user_setting(message.from_user.id, "user_agent", ua)
        await message.reply_to_message.delete()
        await message.reply_text("✅ Saved user_agent and securely deleted your original message.")

    @app.on_message(filters.command("setproxy") & is_auth & filters.reply)
    async def set_proxy(client, message):
        proxy = message.reply_to_message.text.strip()
        await database.update_user_setting(message.from_user.id, "proxy", proxy)
        await message.reply_to_message.delete()
        await message.reply_text("✅ Saved proxy and securely deleted your original message.")

    @app.on_message(filters.text & is_auth & filters.regex(r'http[s]?://'))
    async def handle_url(client, message):
        url = message.text.strip()
        await queue_manager.download_queue.put({'message': message, 'url': url})
        pos = queue_manager.download_queue.qsize()
        await message.reply_text(f"✅ Added to queue. Position: {pos}")

    @app.on_message(filters.document & is_owner & filters.private)
    async def route_upload(client, message):
        if message.caption and "#ROUTING_ID_" in message.caption:
            lines = message.caption.split('\n')
            target_chat = None
            clean_caption = []
            for line in lines:
                if line.startswith("#ROUTING_ID_"):
                    try:
                        target_chat = int(line.replace("#ROUTING_ID_", "").strip())
                    except:
                        pass
                else:
                    clean_caption.append(line)
            
            if target_chat:
                await message.copy(chat_id=target_chat, caption="\n".join(clean_caption).strip())
