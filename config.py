"""
Конфигурация бота
"""
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Константы
BOT_TOKEN = os.getenv('BOT_TOKEN')


# Проверяем наличие токена
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения!")
