import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_NAME = os.getenv("NAME", "Habify")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден")
