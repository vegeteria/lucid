import aiosqlite

DB_PATH = "/app/data/users.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                cf_clearance TEXT,
                user_agent TEXT,
                proxy TEXT
            )
        ''')
        await db.commit()

async def get_user_settings(user_id):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT cf_clearance, user_agent, proxy FROM users WHERE user_id = ?', (user_id,)) as cursor:
            return await cursor.fetchone()

async def update_user_setting(user_id, field, value):
    valid_fields = ["cf_clearance", "user_agent", "proxy"]
    if field not in valid_fields: return
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('INSERT OR IGNORE INTO users (user_id) VALUES (?)', (user_id,))
        await db.execute(f'UPDATE users SET {field} = ? WHERE user_id = ?', (value, user_id))
        await db.commit()
