"""
Клавиатуры главного меню
"""
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_menu_keyboard():
    """Создает клавиатуру главного меню"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Мои привычки"),
            KeyboardButton(text="➕ Добавить привычку")],
            [KeyboardButton(text="📈 Статистика"),
            KeyboardButton(text="⚙️ Настройки")
            ],
            [KeyboardButton(text="❓ Помощь")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard
