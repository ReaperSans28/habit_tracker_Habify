from aiogram.utils.keyboard import InlineKeyboardBuilder

def start():
    kb = InlineKeyboardBuilder()
    kb.button(text="✏️ Создать привычку", callback_data="create_habit")
    kb.button(text="📒 Редактировать привычку", callback_data="edit_habit")
    kb.button(text="📦 Привычки", callback_data="list_habit")
    kb.button(text="🚫 Удалить привычки", callback_data="remove_habit")
    kb.button(text="✉️ Помощь", callback_data="help")
    kb.adjust(2, 2, 1)
    return kb.as_markup()