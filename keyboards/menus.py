# menus.py
# Все клавиатуры бота
from typing import List, Tuple
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup


# ============================================================================
# ONBOARDING MENU
# Используется при создании первой привычки пользователем
# Схема: ONB["Онбординг<br>onboarding_intro<br>кнопка: Создать первую привычку"]
# ============================================================================
def onboarding() -> InlineKeyboardMarkup:
    """
    Single button to create first habit.
    """
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Создать первую привычку", callback_data="habit:create")
    kb.adjust(1)
    return kb.as_markup()


# ============================================================================
# MAIN MENU
# Схема: MM["Главное меню<br>Мои привычки<br>Добавить новую<br>Помощь"]
# Кнопки: "Мои привычки" → habit:list
#          "Добавить новую" → habit:create
#          "Помощь" → help
# ============================================================================
def main_menu() -> InlineKeyboardMarkup:
    """
    Основное меню бота.
    """
    kb = InlineKeyboardBuilder()
    kb.button(text="📦 Мои привычки", callback_data="habit:list")
    kb.button(text="➕ Добавить новую", callback_data="habit:create")
    kb.button(text="✉️ Помощь", callback_data="help")
    kb.adjust(1)  # All buttons in column
    return kb.as_markup()


# ============================================================================
# MY HABITS (Список привычек)
# Используется когда пользователь нажимает "Мои привычки" из главного меню
# Схема: HLIST["Список привычек"]
#         HLIST -- Открыть привычку --> OPEN
#         HLIST -- Назад --> MM
# ============================================================================
def my_habits(habits: List[Tuple[int, str, bool, str]]) -> InlineKeyboardMarkup:
    """
    Список привычек пользователя и кнопка "назад".
    
    Аргументы:
        habits: Список кортежей (habit_id, name, is_active, reminder_time)
                из db.habits.list_habits()

    Возвращает:
        Клавиатура с кнопками привычек + кнопка "назад"
    """
    kb = InlineKeyboardBuilder()
    
    # Add button for each habit
    for habit_id, name, is_active, reminder_time in habits:
        # Prefix based on active status
        prefix = "✅" if is_active else "⏸"
        # Show reminder time if exists
        label = f"{prefix} {name}"
        if reminder_time:
            label += f" • {reminder_time}"
        
        kb.button(text=label, callback_data=f"habit:open:{habit_id}")
    
    # Back to main menu
    kb.button(text="◀️ Назад", callback_data="home")
    
    # All buttons in single column
    kb.adjust(1)
    return kb.as_markup()


# ============================================================================
# HABIT CARD (Карточка привычки)
# Используется когда пользователь открывает конкретную привычку
# Схема: OPEN["Карточка привычки<br>Отметить выполнение<br>Редактировать<br>
#              Пауза/Включить<br>Удалить<br>Назад"]
# Кнопки:  "Отметить выполнение" → habit:check:{hid}
#          "Редактировать" → habit:edit:{hid}
#          "Пауза"/"Включить" → habit:deactivate/activate:{hid}
#          "Удалить" → habit:delete_confirm:{hid}
#          "Назад" → habit:list
# ============================================================================
def habit_card(habit_id: int, is_active: bool) -> InlineKeyboardMarkup:
    """
    Habit card with action buttons.
    
    Args:
        habit_id: ID of the habit
        is_active: Whether habit is active (determines Pause/Activate button)
    
    Returns:
        Keyboard with 5 action buttons
    """
    kb = InlineKeyboardBuilder()
    
    # 1. Mark as done
    kb.button(text="✔️ Отметить выполнение", callback_data=f"habit:check:{habit_id}")
    
    # 2. Edit habit
    kb.button(text="✏️ Редактировать", callback_data=f"habit:edit:{habit_id}")
    
    # 3. Pause/Activate toggle
    if is_active:
        kb.button(text="⏸ Пауза", callback_data=f"habit:deactivate:{habit_id}")
    else:
        kb.button(text="▶️ Включить", callback_data=f"habit:activate:{habit_id}")
    
    # 4. Delete
    kb.button(text="🗑 Удалить", callback_data=f"habit:delete_confirm:{habit_id}")
    
    # 5. Back to list
    kb.button(text="◀️ Назад", callback_data="habit:list")
    
    # Layout: all in column
    kb.adjust(1)
    return kb.as_markup()


# ============================================================================
# DELETE CONFIRMATION (Подтверждение удаления привычки)
# Используется когда: Пользователь нажимает кнопку удаления на карточке привычки
# Схема: CONF["Подтверждение удаления"]
#         CONF -- Удалить --> DELETE
#         CONF -- Отмена --> OPEN
# ============================================================================
def confirm_delete(habit_id: int) -> InlineKeyboardMarkup:
    """
    Confirmation dialog for habit deletion.
    
    Args:
        habit_id: ID of habit to delete
    
    Returns:
        Keyboard with Delete and Cancel buttons
    """
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Удалить", callback_data=f"habit:delete:{habit_id}")
    kb.button(text="◀️ Отмена", callback_data=f"habit:open:{habit_id}")
    kb.adjust(2)  # Две кнопки в ряд
    return kb.as_markup()
