import asyncio
import time
import os
import shutil
import json
from bot import config, database, lucida_wrapper
from pyrogram.errors import MessageNotModified, FloodWait

async def get_audio_info(file_path):
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", file_path
    ]
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        data = json.loads(stdout)
        
        fmt = data.get("format") or {}
        duration = float(fmt.get("duration") or 0)
        mins = int(duration // 60)
        secs = int(duration % 60)
        duration_str = f"{mins}:{secs:02d}"
        
        tags = fmt.get("tags") or {}
        has_lyrics = any(k.lower() in ['lyrics', 'unsyncedlyrics', 'sylt', 'uslt'] for k in tags.keys())
        if not has_lyrics:
            for stream in data.get("streams") or []:
                stream_tags = stream.get("tags") or {}
                if any(k.lower() in ['lyrics', 'unsyncedlyrics', 'sylt', 'uslt'] for k in stream_tags.keys()):
                    has_lyrics = True
                    break
        
        lyrics_str = "Available" if has_lyrics else "Unavailable"
        
        return duration_str, lyrics_str
    except Exception as e:
        print(f"Error getting audio info: {e}")
        return "Unknown", "Unknown"

download_queue = asyncio.Queue()

async def upload_progress(current, total, status_msg, current_track, total_tracks):
    now = time.time()
    if not hasattr(status_msg, "last_progress_time"):
        status_msg.last_progress_time = 0
    if now - status_msg.last_progress_time < 3:
        return
    status_msg.last_progress_time = now
    
    percent = current * 100 / total
    filled = int(percent / 5)
    bar = '█' * filled + '░' * (20 - filled)
    
    mb_current = current / (1024 * 1024)
    mb_total = total / (1024 * 1024)
    
    text = f"📤 **Uploading track {current_track}/{total_tracks}**\n"
    text += f"[{bar}] {percent:.1f}%\n"
    text += f"`{mb_current:.1f}MB / {mb_total:.1f}MB`"
    
    try:
        await status_msg.edit_text(text)
    except:
        pass

async def process_queue(bot_client, user_client):
    while True:
        task = await download_queue.get()
        message = task['message']
        url = task['url']
        user_id = message.from_user.id
        
        status_msg = await bot_client.send_message(message.chat.id, "⏳ Processing starting...", reply_to_message_id=message.id)
        
        settings = await database.get_user_settings(user_id)
        cf_clearance, user_agent, proxy = settings if settings else (None, None, None)
        
        last_update = time.time()
        last_text = ""
        retry_count = 0
        
        async def progress_cb(log_line):
            nonlocal last_update, last_text, retry_count
            print(f"[LUCIDA-BIN] {log_line}", flush=True)
            
            display_text = None
            if "stuck for 30 seconds" in log_line:
                retry_count += 1
                display_text = f"⏳ **Ripping... (Retry {retry_count})**\n`The server is under heavy load.`"
            elif any(k in log_line.lower() for k in ["downloading", "completed", "ripping", "error", "metadata"]):
                display_text = f"⏳ **Downloading...**\n`{log_line[-100:]}`"
            
            if display_text:
                now = time.time()
                if display_text != last_text and (now - last_update) >= config.PROGRESS_UPDATE_DELAY:
                    try:
                        await status_msg.edit_text(display_text)
                        last_update = now
                        last_text = display_text
                    except MessageNotModified:
                        pass
                    except FloodWait as e:
                        await asyncio.sleep(e.value)

        await status_msg.edit_text("⏳ Starting lucida-downloader...")
        temp_dir, code = await lucida_wrapper.run_lucida(url, cf_clearance, user_agent, proxy, progress_cb)
        
        if code != 0:
            await status_msg.edit_text("❌ Download failed. Check your cf_clearance or proxy credentials.")
        else:
            await status_msg.edit_text("✅ Download complete! Uploading to Telegram...")
            files_to_upload = []
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith(".flac") or file.endswith(".mp3"):
                        files_to_upload.append(os.path.join(root, file))
            
            if not files_to_upload:
                await status_msg.edit_text("❌ No audio files found in output.")
            else:
                files_to_upload.sort()
                bot_info = await bot_client.get_me()
                
                for idx, file_path in enumerate(files_to_upload):
                    try:
                        await status_msg.edit_text(f"📤 Uploading track {idx+1}/{len(files_to_upload)}...")
                        
                        target_chat = message.chat.id
                        bot_info = await bot_client.get_me()
                        
                        duration, lyrics = await get_audio_info(file_path)
                        
                        # Always upload to the Bot first via User Client to bypass 50MB limit
                        # We embed the target chat ID in the caption so the bot can route it!
                        routing_caption = f"🎵 Uploaded via Lucida Bot\nDuration: {duration}\nLyrics: {lyrics}\n\n#ROUTING_ID_{target_chat}"
                        
                        await user_client.send_document(
                            chat_id=bot_info.username,
                            document=file_path,
                            caption=routing_caption,
                            progress=upload_progress,
                            progress_args=(status_msg, idx+1, len(files_to_upload))
                        )
                        
                        # The bot's on_message handler in handlers.py will catch this and forward it!
                                    
                    except Exception as e:
                        print(f"Upload error: {e}")
                        await bot_client.send_message(message.chat.id, f"❌ Failed to upload `{os.path.basename(file_path)}`: {e}")
                
                await status_msg.delete()
        
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            
        download_queue.task_done()
