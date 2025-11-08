# handlers/habits.py
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import json

from keyboards import menus as menu
from database.database import db
from handlers.messages import render_message
from utils.habit_format_validator import habit_format_validator
from utils.time_day_parser import time_day_parser

habits_router = Router()


# ============================================================================
# FSM STATES
# ============================================================================
class HabitEdit(StatesGroup):
    """FSM state for habit editing"""
    waiting_for_input = State()


# ============================================================================
# RETURN TO MAIN MENU
# Callback: "home"
# Schema: HLIST -- Назад --> MM
# ============================================================================
@habits_router.callback_query(F.data == "home")
async def return_to_main_menu(callback: CallbackQuery):
    """Return to main menu from habit list"""
    reply = menu.main_menu()
    assert callback.message
    await callback.message.answer("Главное меню:", reply_markup=reply)
    await callback.answer()


# ============================================================================
# HABIT LIST - Show all habits
# Callback: "habit:list"
# Schema: MM -- Мои привычки --> HLIST
# ============================================================================
@habits_router.callback_query(F.data == "habit:list")
async def list_habits_cb(callback: CallbackQuery):
    """Show list of all user's habits"""
    uid = callback.from_user.id
    
    # Get habits from database: [(habit_id, name, is_active, reminder_time), ...]
    habits = db.habits.list_habits(uid)
    
    reply = menu.my_habits(habits)
    assert callback.message
    await callback.message.answer("Мои привычки:", reply_markup=reply)
    await callback.answer()


# ============================================================================
# OPEN HABIT CARD
# Callback: "habit:open:{habit_id}"
# Schema: HLIST -- Открыть привычку --> OPEN
# ============================================================================
@habits_router.callback_query(F.data.startswith("habit:open:"))
async def open_habit(cb: CallbackQuery):
    """Open habit card with action buttons"""
    assert cb.data
    hid = int(cb.data.split(":")[-1])
    h = db.habits.get_habit(hid)
    
    if not h:
        await cb.answer("Привычка не найдена")
        return
    
    # Convert is_active to bool
    is_active = bool(int(h["is_active"])) if isinstance(h["is_active"], str) else bool(h["is_active"])
    
    # Format habit card message
    habit_text = f"**{h['name']}**\n{h['description']}\n\n⏰ {h['reminder_time']}"
    
    reply = menu.habit_card(habit_id=hid, is_active=is_active)
    assert cb.message
    await cb.message.answer(habit_text, reply_markup=reply, parse_mode="Markdown")
    await cb.answer()


# ============================================================================
# MARK HABIT AS DONE
# Callback: "habit:check:{habit_id}"
# Schema: OPEN -- Отметить --> ACTION --> OPEN
# ============================================================================
@habits_router.callback_query(F.data.startswith("habit:check:"))
async def check_habit(cb: CallbackQuery):
    """Mark habit as completed for today"""
    assert cb.data
    hid = int(cb.data.split(":")[-1])
    
    # Get today's date
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    
    # Record completion
    db.habit_actions.add_action(hid, today, True)
    
    await cb.answer("✅ Отмечено!")
    # Refresh the card
    await open_habit(cb)


# ============================================================================
# TOGGLE HABIT ACTIVE/PAUSED
# Callbacks: "habit:deactivate:{habit_id}", "habit:activate:{habit_id}"
# Schema: OPEN -- Пауза/Включить --> TOGGLE --> OPEN
# ============================================================================
@habits_router.callback_query(F.data.startswith("habit:deactivate:"))
async def deactivate_habit(cb: CallbackQuery):
    """Pause habit"""
    assert cb.data
    hid = int(cb.data.split(":")[-1])
    db.habits.change_active(hid, False)
    await cb.answer("Привычка на паузе")
    await open_habit(cb)


@habits_router.callback_query(F.data.startswith("habit:activate:"))
async def activate_habit(cb: CallbackQuery):
    """Activate habit"""
    assert cb.data
    hid = int(cb.data.split(":")[-1])
    db.habits.change_active(hid, True)
    await cb.answer("Привычка активна")
    await open_habit(cb)


# ============================================================================
# DELETE HABIT - Confirmation flow
# Callbacks: "habit:delete_confirm:{habit_id}", "habit:delete:{habit_id}"
# Schema: OPEN -- Удалить --> CONF -- Удалить --> DELETE --> HLIST
# ============================================================================
@habits_router.callback_query(F.data.startswith("habit:delete_confirm:"))
async def delete_confirm(cb: CallbackQuery):
    """Show delete confirmation dialog"""
    assert cb.data
    hid = int(cb.data.split(":")[-1])
    reply = menu.confirm_delete(hid)
    assert cb.message
    await cb.message.answer("Уверен? Отменить будет невозможно.", reply_markup=reply)
    await cb.answer()


@habits_router.callback_query(F.data.startswith("habit:delete:"))
async def delete_habit(cb: CallbackQuery):
    """Delete habit and return to list"""
    assert cb.data
    hid = int(cb.data.split(":")[-1])
    db.habits.delete(hid)
    
    # Return to habit list
    uid = cb.from_user.id
    habits = db.habits.list_habits(uid)
    
    assert cb.message
    await cb.message.answer("Мои привычки:", reply_markup=menu.my_habits(habits))
    await cb.answer("🗑 Удалено")


# ============================================================================
# EDIT HABIT - Re-enter habit in same format
# Callback: "habit:edit:{habit_id}"
# Schema: OPEN -- Редактировать --> HP (habit_prompt state)
# ============================================================================
@habits_router.callback_query(F.data.startswith("habit:edit:"))
async def start_habit_edit(callback: CallbackQuery, state: FSMContext):
    """
    Start habit editing flow.
    User will re-enter habit in the same format: "название -- описание -- время и дни"
    """
    assert callback.data
    hid = int(callback.data.split(":")[-1])
    
    # Store habit_id in FSM context for later
    await state.update_data(editing_habit_id=hid)
    
    # Get user info for message rendering
    user_id = callback.from_user.id if callback.from_user else None
    if not user_id:
        await callback.answer("Ошибка: не удалось определить пользователя")
        return
    
    user = db.users.get_user(user_id)
    if not user:
        await callback.answer("Ошибка: пользователь не найден в базе")
        return
    
    username = user["first_name"]
    gender = user["gender"]
    
    # Set FSM state to wait for input
    await state.set_state(HabitEdit.waiting_for_input)
    
    # Send prompt message for editing
    prompt_msg = render_message("habit_prompt_edit", username, gender)
    
    if callback.message:
        await callback.message.answer(prompt_msg)
    
    await callback.answer()


@habits_router.message(HabitEdit.waiting_for_input)
async def process_habit_edit(message: Message, state: FSMContext):
    """
    Process edited habit input.
    Validates format, parses data, updates habit in database.
    """
    user_id = message.from_user.id if message.from_user else None
    if not user_id:
        await message.answer("Ошибка: не удалось определить пользователя")
        return
    
    # Get user for gender
    user = db.users.get_user(user_id)
    if not user:
        await message.answer("Ошибка: пользователь не найден")
        return
    
    username = user["first_name"]
    gender = user["gender"]
    
    user_input = message.text if message.text else ""
    
    # Step 1: Validate and split format
    format_valid, format_data, format_error = habit_format_validator.validate_and_split(user_input)
    
    if not format_valid:
        error_key = habit_format_validator.get_error_key(format_error or "unknown")
        error_msg = render_message(error_key, username, gender)
        await message.answer(error_msg)
        return
    
    # Extract parts
    assert format_data is not None
    habit_name = format_data["name"]
    habit_description = format_data["description"]
    schedule_str = format_data["schedule"]
    
    # Step 2: Parse time and days
    schedule_valid, schedule_data, schedule_error = time_day_parser.parse(schedule_str)
    
    if not schedule_valid:
        error_key = time_day_parser.get_error_key(schedule_error or "unknown")
        error_msg = render_message(error_key, username, gender)
        await message.answer(error_msg)
        return
    
    # Extract schedule data
    assert schedule_data is not None
    reminder_time = schedule_data["time"]
    days_json = schedule_data["days_json"]
    
    # Step 3: Get habit_id from FSM context
    data = await state.get_data()
    habit_id = data.get("editing_habit_id")
    
    if not habit_id:
        await message.answer("Ошибка: не удалось определить редактируемую привычку")
        await state.clear()
        return
    
    # Step 4: Update habit in database
    try:
        db.habits.edit_habit(
            habit_id=habit_id,
            name=habit_name,
            description=habit_description,
            reminder_time=reminder_time,
            schedule_days=days_json
        )
        
        # Step 5: Send success message and show habit card
        days_dict = json.loads(days_json)
        active_days = [day for day, active in days_dict.items() if active]
        
        day_names_ru = {
            "mon": "пн", "tue": "вт", "wed": "ср", "thu": "чт",
            "fri": "пт", "sat": "сб", "sun": "вс"
        }
        
        if len(active_days) == 7:
            days_str = "ежедневно"
        else:
            days_str = ", ".join([day_names_ru[day] for day in active_days])
        
        success_msg = render_message(
            "habit_success", 
            username, 
            gender,
            habit_name=habit_name,
            reminder_time=reminder_time,
            days_str=days_str
        )
        
        await message.answer(success_msg)
        
        # Clear FSM state
        await state.clear()
        
        # Show updated habit card
        h = db.habits.get_habit(habit_id)
        if h:
            is_active = bool(int(h["is_active"])) if isinstance(h["is_active"], str) else bool(h["is_active"])
            reply = menu.habit_card(habit_id=habit_id, is_active=is_active)
            await message.answer("Карточка привычки:", reply_markup=reply)
        
    except Exception as e:
        error_msg = f"❌ Ошибка при обновлении привычки: {str(e)}"
        await message.answer(error_msg)
        return


# ============================================================================
# HELP HANDLER
# Callback: "help"
# Схема: MM -- Помощь --> (help screen)
# ============================================================================
@habits_router.callback_query(F.data == "help")
async def show_help(callback: CallbackQuery):
    """
    Справка по использованию бота.
    """

    help_text = (
        "📖 **Справка**\n\n"
        "Ты хочешь разобраться в правилах. Похвально. Постараюсь быть прямолинейной.\n\n"
        "**Как добавить привычку:**\n"
        "`название -- описание -- время и дни`\n\n"
        "**Примеры:**\n"
        "• `Бег -- Пробежка 5км -- 6:30 ежедневно`\n"
        "• `Чтение -- 20 страниц -- 21:00 пн, ср, пт`\n"
        "• `Медитация -- 10 минут тишины -- 7:00 пн-пт`\n\n"
        "**О времени:** `6:30`, `18:45`, `6:30 am`, `9:00 pm` — я понимаю все эти формы.\n\n"
        "**О днях:** `ежедневно`, `пн-пт`, `пн, ср, пт`, `daily`, `mon, wed, fri`.\n\n"
        "Кнопки тоже работают. Если их боишься — можно всё вводить вручную.\n"
        "**безэмоционально** Я фиксирую. Остальное — твоя дисциплина."
    )    
        
    await callback.answer()
    assert callback.message
    await callback.message.answer(help_text, parse_mode="Markdown")

