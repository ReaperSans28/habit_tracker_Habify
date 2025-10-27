import json
import os
from aiogram.types import Message
from aiogram.filters import Command
from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

commands_router = Router()

class HabitStates(StatesGroup):
    waiting_for_habit_text = State()
    waiting_for_habit_image = State()

@commands_router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды start"""
    welcome_text = (
        f"Привет, {message.from_user.first_name}.\n"
        f"Я бот для трекинга твоих привычек\n"
        f"Если нужна помощь -> /help"
        f"Добавить свою первую привычку - /add_habit"
    )
    await message.answer(welcome_text)


@commands_router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды help"""
    welcome_text = (
        f"Команды бота:\n"
        f"/start - запуск / перезагрузка бота\n"
        f"/add_habit - добавить новую привычку\n"
        f"/habits - посмотреть все привычки"
    )
    await message.answer(welcome_text)


@commands_router.message(Command("add_habit"))
async def cmd_add_habit(message: Message, state: FSMContext):
    """Обработчик команды add_habit"""
    await state.set_state(HabitStates.waiting_for_habit_text)
    await message.answer(
        "Отправьте мне название и описание привычки в текстовом виде.\n"
        "Например: 'Читать книги - читать 30 минут каждый день'"
    )


@commands_router.message(Command("habits"))
async def cmd_habits(message: Message):
    """Обработчик команды habits - показать все привычки"""
    try:
        with open("data/habits.json", "r", encoding="utf-8") as f:
            habits_data = json.load(f)
        
        user_id = str(message.from_user.id)
        
        if user_id not in habits_data or not habits_data[user_id]:
            await message.answer("У вас пока нет добавленных привычек.")
            return
        
        habits = habits_data[user_id]
        await message.answer(f"У вас {len(habits)} привычек:\n")
        
        # Отправляем каждую привычку отдельным сообщением
        for i, habit in enumerate(habits, 1):
            habit_text = (
                f"📋 Привычка {i}:\n"
                f"Название: {habit['name']}\n"
                f"Описание: {habit['description']}\n"
                f"Дата добавления: {habit['created_at']}"
            )
            
            # Если есть изображение, отправляем его с текстом
            if habit.get('image_path') and os.path.exists(habit['image_path']):
                try:
                    with open(habit['image_path'], 'rb') as photo:
                        await message.answer_photo(
                            photo=photo,
                            caption=habit_text
                        )
                except Exception as e:
                    # Если не удалось отправить изображение, отправляем только текст
                    await message.answer(habit_text + f"\n\n⚠️ Ошибка загрузки изображения: {e}")
            else:
                # Если нет изображения, отправляем только текст
                await message.answer(habit_text)

    except FileNotFoundError:
        await message.answer("Файл с привычками не найден.")
    except Exception as e:
        await message.answer(f"Ошибка при загрузке привычек: {e}")
