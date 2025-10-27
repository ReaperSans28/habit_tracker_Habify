"""
Конфигурация бота
"""
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Константы
BOT_TOKEN = os.getenv('BOT_TOKEN')
QUOTES_URL = os.getenv('QUOTES_URL')

# Настройки бота
BOT_NAME = os.getenv('BOT_NAME', 'HabitTracker')
BOT_DESCRIPTION = os.getenv('BOT_DESCRIPTION', 'Бот для отслеживания привычек')

# Проверяем наличие токена
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения!")
