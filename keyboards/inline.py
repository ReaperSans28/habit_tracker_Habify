"""
Inline клавиатуры
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_habit_actions_keyboard(habit_id: int):
    """
    Клавиатура действий с привычкой (выполнено / пропущено / редактировать / удалить / статистика)
    """
    builder = InlineKeyboardBuilder()

    # Добавляем ID привычки в callback_data
    builder.button(text="✅ Выполнено", callback_data=f"habit_done_{habit_id}")
    builder.button(text="❌ Пропущено", callback_data=f"habit_skip_{habit_id}")
    builder.button(text="✏️ Редактировать", callback_data=f"habit_edit_{habit_id}")
    builder.button(text="🗑️ Удалить", callback_data=f"habit_delete_{habit_id}")
    builder.button(text="📊 Статистика", callback_data=f"habit_stats_{habit_id}")

    # Располагаем кнопки: 2 + 2 + 1
    builder.adjust(2, 2, 1)

    return builder.as_markup()

def back():
    back = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️", callback_data="back")]
    ])
    return back


def get_confirmation_keyboard(action: str, item_id: int = None):
    """
    Клавиатура подтверждения действия (Да / Нет)
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да", callback_data=f"confirm_{action}_{item_id}")],
            [InlineKeyboardButton(text="❌ Нет", callback_data=f"cancel_{action}_{item_id}")]
        ]
    )
    return keyboard



def get_habit_list_keyboard(habits=None):
    """
    Клавиатура списка привычек.
    habits: список либо кортежей (id, name), либо просто названий привычек.
    """
    if not habits:
        habits = ["Читать 30 минут", "Пить воду 8 стаканов в день"]

    keyboard_buttons = []

    for idx, item in enumerate(habits):
        # Если элемент — кортеж (id, name)
        if isinstance(item, tuple) and len(item) >= 2:
            habit_id, habit_name = item[:2]
        else:  # если просто строка
            habit_id, habit_name = idx, str(item)

        keyboard_buttons.append([
            InlineKeyboardButton(
                text=f"📝 {habit_name}",
                callback_data=f"select_habit_{habit_id}"
            )
        ])

    # Кнопка добавления новой привычки
    keyboard_buttons.append([
        InlineKeyboardButton(text="➕ Добавить новую привычку", callback_data="add_new_habit")
    ])

    return InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)



