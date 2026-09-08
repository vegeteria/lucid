import asyncio
import logging
from pyrogram import Client, compose
from bot import config, database, handlers, queue_manager

logging.basicConfig(level=logging.INFO)

async def main():
    print("Initializing Database...")
    await database.init_db()
    
    print("Starting bot_client...")
    bot_client = Client(
        "bot_session",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        bot_token=config.BOT_TOKEN,
        workdir="/app/data"
    )
    
    print("Starting user_client...")
    user_client = Client(
        "user_session",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        session_string=config.USER_SESSION_STRING,
        workdir="/app/data"
    )
    
    handlers.register_handlers(bot_client)
    
    print("Starting background queue processor...")
    asyncio.create_task(queue_manager.process_queue(bot_client, user_client))
    
    print("Bot is up and running!")
    await compose([bot_client, user_client])

if __name__ == "__main__":
    asyncio.run(main())
