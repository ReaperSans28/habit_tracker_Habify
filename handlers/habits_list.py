"""
Хэндлеры для просмотра списка привычек с пагинацией и детальной информацией
"""
from aiogram import F, Router
from aiogram.types import CallbackQuery
import json

import database.database as db
import keyboards.inline as kb

habits_list_router = Router()


def format_habit_detail(habit: dict) -> str:
    """
    Форматирует информацию о привычке для отображения.
    
    Args:
        habit: словарь с данными привычки из БД
    
    Returns:
        Отформатированная строка с информацией о привычке
    """
    name = habit.get('name', 'Без названия')
    description = habit.get('description', 'Нет описания')
    created_at = habit.get('created_at', 'Неизвестно')
    reminder_time = habit.get('reminder_time', 'Не указано')
    schedule_days = habit.get('schedule_days', '[]')
    streak_count = habit.get('streak_count', 0)
    longest_streak = habit.get('longest_streak', 0)
    is_active = habit.get('is_active', False)

    try:
        days_dict = json.loads(schedule_days) if schedule_days else {}
        day_names_ru = {
            "mon": "пн", "tue": "вт", "wed": "ср", "thu": "чт",
            "fri": "пт", "sat": "сб", "sun": "вс"
        }
        active_days = [day_names_ru.get(day, day) for day, active in days_dict.items() if active]
        
        if len(active_days) == 7:
            days_str = "ежедневно"
        elif len(active_days) == 0:
            days_str = "не указано"
        else:
            days_str = ", ".join(active_days)
    except (json.JSONDecodeError, TypeError):
        days_str = "не указано"

    try:
        if created_at and created_at != 'Неизвестно':
            from datetime import datetime
            if isinstance(created_at, str):
                # Пытаемся распарсить дату
                try:
                    dt = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    created_at = dt.strftime('%d.%m.%Y')
                except:
                    created_at = str(created_at)[:10]
    except:
        pass
    
    status = "✅ Активна" if is_active else "❌ Неактивна"
    
    text = f"""📌 **{name}**

📝 Описание: {description}

📅 Дата создания: {created_at}
⏰ Время напоминания: {reminder_time}
📆 Дни выполнения: {days_str}

🔥 Текущая серия: {streak_count}
🏆 Самая длинная серия: {longest_streak}

{status}"""
    
    return text


@habits_list_router.callback_query(F.data == "list_habit")
async def show_habits_list(callback: CallbackQuery):
    """Показывает список привычек пользователя (первая страница)"""
    user_id = callback.from_user.id if callback.from_user else None
    if not user_id:
        await callback.answer("❌ Ошибка: не удалось определить пользователя.", show_alert=True)
        return

    active_habits = db.get_active_habits(user_id)
    
    if active_habits.empty:
        try:
            await callback.message.edit_text("📦 У вас пока нет активных привычек.")
        except:
            await callback.message.answer("📦 У вас пока нет активных привычек.")
        await callback.answer()
        return

    try:
        await callback.message.edit_text(
            "📦 Ваш список привычек ⬇️:",
            reply_markup=kb.habits_list(active_habits, page=0)
        )
    except Exception:
        await callback.message.answer(
            "📦 Ваш список привычек ⬇️:",
            reply_markup=kb.habits_list(active_habits, page=0)
        )
    await callback.answer()


@habits_list_router.callback_query(F.data.startswith("habits_page:"))
async def handle_habits_pagination(callback: CallbackQuery):
    """Обрабатывает пагинацию списка привычек"""
    user_id = callback.from_user.id if callback.from_user else None
    if not user_id:
        await callback.answer("❌ Ошибка: не удалось определить пользователя.", show_alert=True)
        return

    try:
        page = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        await callback.answer("❌ Ошибка: неверный номер страницы.", show_alert=True)
        return

    active_habits = db.get_active_habits(user_id)
    
    if active_habits.empty:
        await callback.message.edit_text("📦 У вас пока нет активных привычек.")
        await callback.answer()
        return

    per_page = 5
    total_pages = (len(active_habits) + per_page - 1) // per_page
    if page < 0 or page >= total_pages:
        await callback.answer("❌ Страница не найдена.", show_alert=True)
        return

    try:
        await callback.message.edit_text(
            "📦 Ваш список привычек ⬇️:",
            reply_markup=kb.habits_list(active_habits, page=page)
        )
    except Exception:
        await callback.message.answer(
            "📦 Ваш список привычек ⬇️:",
            reply_markup=kb.habits_list(active_habits, page=page)
        )
    await callback.answer()


@habits_list_router.callback_query(F.data.startswith("habit_detail:"))
async def show_habit_detail(callback: CallbackQuery):
    """Показывает детальную информацию о привычке"""
    user_id = callback.from_user.id if callback.from_user else None
    if not user_id:
        await callback.answer("❌ Ошибка: не удалось определить пользователя.", show_alert=True)
        return

    try:
        habit_id = int(callback.data.split(":")[1])
    except (ValueError, IndexError):
        await callback.answer("❌ Ошибка: неверный ID привычки.", show_alert=True)
        return

    habit = db.get_habit_by_id(habit_id)
    
    if not habit:
        await callback.answer("❌ Привычка не найдена.", show_alert=True)
        return

    if habit.get('telegram_id') != user_id:
        await callback.answer("❌ У вас нет доступа к этой привычке.", show_alert=True)
        return

    habit_text = format_habit_detail(habit)
    
    try:
        await callback.message.edit_text(
            habit_text,
            reply_markup=kb.habit_detail(habit_id),
            parse_mode="Markdown"
        )
    except Exception:
        await callback.message.answer(
            habit_text,
            reply_markup=kb.habit_detail(habit_id),
            parse_mode="Markdown"
        )
    await callback.answer()


@habits_list_router.callback_query(F.data == "habits_page_info")
async def habits_page_info(callback: CallbackQuery):
    """Заглушка для кнопки информации о странице (не делает ничего)"""
    await callback.answer()
