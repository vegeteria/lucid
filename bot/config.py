import os
import dotenv

ENV_PATH = "/app/.env"
dotenv.load_dotenv(ENV_PATH)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
API_ID = int(os.environ.get("API_ID", "0"))
API_HASH = os.environ.get("API_HASH", "")
USER_SESSION_STRING = os.environ.get("USER_SESSION_STRING", "")
OWNER_ID = int(os.environ.get("OWNER_ID", "0"))
PROGRESS_UPDATE_DELAY = int(os.environ.get("PROGRESS_UPDATE_DELAY", "15"))

def get_authorized_users():
    dotenv.load_dotenv(ENV_PATH, override=True)
    auth_str = os.environ.get("AUTHORIZED_USERS", "")
    if not auth_str.strip():
        return [OWNER_ID]
    return list(set([int(x.strip()) for x in auth_str.split(",") if x.strip().isdigit()] + [OWNER_ID]))

def add_authorized_user(user_id: int):
    users = get_authorized_users()
    if user_id not in users:
        users.append(user_id)
        dotenv.set_key(ENV_PATH, "AUTHORIZED_USERS", ",".join(map(str, users)))

def remove_authorized_user(user_id: int):
    users = get_authorized_users()
    if user_id in users and user_id != OWNER_ID:
        users.remove(user_id)
        dotenv.set_key(ENV_PATH, "AUTHORIZED_USERS", ",".join(map(str, users)))
