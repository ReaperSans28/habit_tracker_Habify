"""
New habit creation handler with simplified format:
"название -- описание -- время и дни"
"""
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import datetime
import json

from database.database import db
from handlers.messages import render_message
from keyboards import menus as menu
from utils.habit_format_validator import habit_format_validator
from utils.time_day_parser import time_day_parser
from utils.name_validator import Gender


habit_create_router = Router()


class HabitCreate(StatesGroup):
    """FSM state for habit creation"""
    waiting_for_input = State()


@habit_create_router.callback_query(F.data == "habit:create")
async def start_habit_creation(callback: CallbackQuery, state: FSMContext):
    """
    Handles the 'habit:create' button click.
    Shows prompt with format explanation and examples.
    """
    # Get user info for message rendering
    user_id = callback.from_user.id if callback.from_user else None
    if not user_id:
        await callback.answer("Ошибка: не удалось определить пользователя")
        return
    
    # Get user from database for gender
    user = db.users.get_user(user_id)
    if not user:
        await callback.answer("Ошибка: пользователь не найден в базе")
        return
    
    username = user["first_name"]
    gender = user["gender"]
    
    # Set FSM state
    await state.set_state(HabitCreate.waiting_for_input)
    
    # Send prompt message
    prompt_msg = render_message("habit_prompt", username, gender)
    
    if callback.message:
        await callback.message.answer(prompt_msg)
    
    await callback.answer()


@habit_create_router.message(HabitCreate.waiting_for_input)
async def process_habit_input(message: Message, state: FSMContext):
    """
    Processes user input for habit creation.
    Validates format, parses data, saves to database.
    """
    user_id = message.from_user.id if message.from_user else None
    if not user_id:
        await message.answer("Ошибка: не удалось определить пользователя")
        return
    
    # Get user for gender
    user = db.users.get_user(user_id)
    if not user:  # Не должно случиться, на всякий случай
        await message.answer("Ошибка: пользователь не найден")
        return
    
    username = user["first_name"]
    gender: Gender = user["gender"]
    
    user_input = message.text if message.text else ""
    
    # Step 1: Validate and split format
    format_valid, format_data, format_error = habit_format_validator.validate_and_split(user_input)
    
    if not format_valid:
        # Get error message key and render
        error_key = habit_format_validator.get_error_key(format_error or "unknown")
        error_msg = render_message(error_key, username, gender)
        await message.answer(error_msg)
        # Keep in same state - user can try again
        return
    
    # Extract parts
    assert format_data is not None
    habit_name = format_data["name"]
    habit_description = format_data["description"]
    schedule_str = format_data["schedule"]
    
    # Step 2: Parse time and days
    schedule_valid, schedule_data, schedule_error = time_day_parser.parse(schedule_str)
    
    if not schedule_valid:
        # Get error message key
        error_key = time_day_parser.get_error_key(schedule_error or "unknown")
        error_msg = render_message(error_key, username, gender)
        await message.answer(error_msg)
        # Keep in same state - user can try again
        return
    
    # Extract schedule data
    assert schedule_data is not None
    reminder_time = schedule_data["time"]
    days_json = schedule_data["days_json"]
    
    # Step 3: Save to database
    try:
        created_at = datetime.datetime.now()
        
        db.habits.add_habit(
            telegram_id=user_id,
            name=habit_name,
            description=habit_description,
            created_at=str(created_at),
            is_active="1",  # SQLite boolean as string
            reminder_time=reminder_time,
            schedule_days=days_json,
            streak_count="0",
            longest_streak="0"
        )
        
        # Step 4: Send success message
        # Format days for display
        days_dict = json.loads(days_json)
        active_days = [day for day, active in days_dict.items() if active]
        
        # Convert to readable format
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
        
        # Return to main menu (Schema: MODE -- Нет --> MM)
        await message.answer("Главное меню:", reply_markup=menu.main_menu())
        
    except Exception as e:
        # Handle database errors
        error_msg = f"❌ Ошибка при сохранении привычки: {str(e)}"
        await message.answer(error_msg)
        # Don't clear state - user can try again
        return
