from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

def backmenu():
    menu = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back")],
    ])
    return menu


def habit():
    menu = InlineKeyboardBuilder()
    menu.button(text="🗓️ Каждый день", callback_data="habit_days")
    menu.button(text="📆 Несколько дней", callback_data="habit_day")
    menu.button(text="🏠 Главное меню", callback_data="back")
    return menu


