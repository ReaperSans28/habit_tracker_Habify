from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import pandas as pd

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


def habits_list(habits_df: pd.DataFrame, page: int = 0, per_page: int = 5) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру со списком привычек для страницы с пагинацией.
    
    Args:
        habits_df: DataFrame с привычками
        page: номер страницы (начиная с 0)
        per_page: количество привычек на странице
    
    Returns:
        InlineKeyboardMarkup с кнопками привычек и навигацией
    """
    kb = InlineKeyboardBuilder()

    if habits_df.empty:
        kb.button(text="🏠 Главное меню", callback_data="back")
        kb.adjust(1)
        return kb.as_markup()

    total_habits = len(habits_df)
    start_idx = page * per_page
    end_idx = min(start_idx + per_page, total_habits)

    page_habits = habits_df.iloc[start_idx:end_idx]

    for _, habit in page_habits.iterrows():
        habit_name = habit.get('name', 'Без названия')
        habit_id = habit.get('habit_id')
        button_text = habit_name[:30] + "..." if len(habit_name) > 30 else habit_name
        kb.button(text=f"📌 {button_text}", callback_data=f"habit_detail:{habit_id}")

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="◀️ Назад", callback_data=f"habits_page:{page - 1}"))
    
    if end_idx < total_habits:
        nav_buttons.append(InlineKeyboardButton(text="Вперёд ▶️", callback_data=f"habits_page:{page + 1}"))
    
    if nav_buttons:
        kb.row(*nav_buttons)

    if total_habits > per_page:
        page_info = f"Страница {page + 1}/{(total_habits + per_page - 1) // per_page}"
        kb.button(text=page_info, callback_data="habits_page_info")

    kb.button(text="🏠 Главное меню", callback_data="back")
    kb.adjust(1)
    
    return kb.as_markup()


def habit_detail(habit_id: int) -> InlineKeyboardMarkup:
    """
    Создает клавиатуру для детального просмотра привычки.
    
    Args:
        habit_id: ID привычки
    
    Returns:
        InlineKeyboardMarkup с кнопками навигации
    """
    kb = InlineKeyboardBuilder()
    kb.button(text="🔙 Назад к списку", callback_data="list_habit")
    kb.button(text="🏠 Главное меню", callback_data="back")
    kb.adjust(1)
    return kb.as_markup()

