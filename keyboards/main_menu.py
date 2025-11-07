# main_menu.py
from typing import Iterable, Optional, Tuple
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup

# ------------------------------------------------------------
# Онбординг: ноль привычек → одна большая кнопка
# ------------------------------------------------------------
def onboarding() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="➕ Создать первую привычку", callback_data="habit:create")
    kb.adjust(1)
    return kb.as_markup()


# ------------------------------------------------------------
# Главное меню (дом)
# - today_count: сколько задач на сегодня (для бейджа)
# - has_habits: есть ли вообще привычки
# - has_active: есть ли активные привычки
# - has_inactive: есть ли выключенные/на паузе
# ------------------------------------------------------------
def home(
    *,
    today_count: int = 0,
    has_habits: bool = False,
    has_active: bool = False,
    has_inactive: bool = False,
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    # На сегодня — если есть привычки: показывает список due today
    if has_habits:
        today_label = f"📌 На сегодня ({today_count})" if today_count > 0 else "📌 На сегодня (0)"
        kb.button(text=today_label, callback_data="today:list")

    # Всегда можно добавить
    kb.button(text="➕ Добавить", callback_data="habit:create")

    # Раздел «Мои привычки»
    if has_habits:
        kb.button(text="📦 Мои привычки", callback_data="habit:list:page:1")

    # Быстрые утилиты — появляются, когда есть привычки
    if has_active or has_inactive:
        kb.button(text="⏰ Напоминания", callback_data="reminders:menu")
        kb.button(text="📈 Статистика", callback_data="stats:menu")

    # Помощь — всегда
    kb.button(text="✉️ Помощь", callback_data="help")

    # Компоновка
    if has_habits:
        if has_active or has_inactive:
            kb.adjust(2, 2, 1)  # [На сегодня, Добавить] [Мои привычки, Напоминания] [Статистика] [Помощь]
        else:
            kb.adjust(2, 1, 1)  # [На сегодня, Добавить] [Мои привычки] [Помощь]
    else:
        kb.adjust(1, 1)        # [Добавить] [Помощь]

    return kb.as_markup()


# ------------------------------------------------------------
# Список привычек (пагинация)
# habits: Iterable[Tuple[habit_id:int, name:str, is_active:bool, reminder:str]]
# page, page_size — для пагинации
# ------------------------------------------------------------
def list_habits(
    habits: Iterable[Tuple[int, str, bool, Optional[str]]],
    *,
    page: int,
    page_size: int = 6,
    total_count: Optional[int] = None,
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    # элементы
    for hid, name, is_active, reminder in habits:
        prefix = "✅" if is_active else "⏸"
        tail = f" • {reminder}" if reminder else ""
        label = f"{prefix} {name}{tail}"
        kb.button(text=label, callback_data=f"habit:open:{hid}")

    # пагинация (если известно total_count)
    if total_count is not None:
        pages = max(1, (total_count + page_size - 1) // page_size)
        prev_page = page - 1 if page > 1 else pages
        next_page = page + 1 if page < pages else 1
        # навигация только если страниц > 1
        if pages > 1:
            kb.button(text="◀️", callback_data=f"habit:list:page:{prev_page}")
            kb.button(text=f"{page}/{pages}", callback_data="noop")
            kb.button(text="▶️", callback_data=f"habit:list:page:{next_page}")
            kb.adjust(*([1] * min(page_size, 3)))  # выровнять последние три (стрелки)
        else:
            kb.adjust(1)
    else:
        kb.adjust(1)

    # назад
    kb.button(text="◀️ Назад", callback_data="home")
    kb.adjust(1)
    return kb.as_markup()


# ------------------------------------------------------------
# Карточка привычки: быстрые действия
# ------------------------------------------------------------
def habit_actions(
    *,
    habit_id: int,
    name: str,
    is_active: bool,
) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    # Выполнить — фикс сегодня
    kb.button(text="✔️ Отметить выполнено", callback_data=f"habit:check:{habit_id}")

    # Расписание / напоминание
    kb.button(text="🗓️ Расписание", callback_data=f"habit:schedule:{habit_id}")
    kb.button(text="⏰ Время", callback_data=f"habit:reminder:{habit_id}")

    # Переименовать
    kb.button(text="✏️ Переименовать", callback_data=f"habit:rename:{habit_id}")

    # Вкл/Пауза
    if is_active:
        kb.button(text="⏸ Пауза", callback_data=f"habit:deactivate:{habit_id}")
    else:
        kb.button(text="▶️ Включить", callback_data=f"habit:activate:{habit_id}")

    # Удалить
    kb.button(text="🗑 Удалить", callback_data=f"habit:delete_confirm:{habit_id}")

    # Назад к списку
    kb.button(text="◀️ К списку", callback_data="habit:list:page:1")

    kb.adjust(1, 2, 2, 1, 1)  # аккуратная сетка
    return kb.as_markup()


# ------------------------------------------------------------
# Подтверждение удаления
# ------------------------------------------------------------
def confirm_delete(habit_id: int, name: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Удалить", callback_data=f"habit:delete:{habit_id}")
    kb.button(text="◀️ Отмена", callback_data=f"habit:open:{habit_id}")
    kb.adjust(2)
    return kb.as_markup()
