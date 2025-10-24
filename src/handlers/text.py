import json
import os
from datetime import datetime
from aiogram.types import Message
from aiogram import Router
from aiogram.fsm.context import FSMContext
from .commands import HabitStates

text_router = Router()

@text_router.message(HabitStates.waiting_for_habit_text)
async def process_habit_text(message: Message, state: FSMContext):
    """Обработка текстового описания привычки"""
    habit_text = message.text.strip()
    
    if not habit_text:
        await message.answer("Пожалуйста, отправьте корректное описание привычки.")
        return
    
    # Сохраняем текст привычки в состояние
    await state.update_data(habit_text=habit_text)
    await state.set_state(HabitStates.waiting_for_habit_image)
    
    await message.answer(
        f"Отлично! Привычка: '{habit_text}'\n\n"
        f"Теперь отправьте изображение для этой привычки (или отправьте 'пропустить' чтобы не добавлять изображение)."
    )


@text_router.message(HabitStates.waiting_for_habit_image)
async def process_habit_image_text(message: Message, state: FSMContext):
    """Обработка текста вместо изображения на этапе добавления изображения"""
    if message.text and message.text.lower() in ['пропустить', 'skip', 'нет', 'no']:
        # Сохраняем привычку без изображения
        data = await state.get_data()
        await save_habit_to_json(message, data['habit_text'], None)
        await state.clear()
        await message.answer("Привычка успешно добавлена без изображения!")
    else:
        await message.answer(
            "Пожалуйста, отправьте изображение или напишите 'пропустить' чтобы не добавлять изображение."
        )


async def save_habit_to_json(message: Message, habit_text: str, image_path: str = None):
    """Сохранение привычки в JSON файл"""
    try:
        # Загружаем существующие данные
        try:
            with open("data/habits.json", "r", encoding="utf-8") as f:
                habits_data = json.load(f)
        except FileNotFoundError:
            habits_data = {}
        
        user_id = str(message.from_user.id)
        
        # Инициализируем массив привычек для пользователя если его нет
        if user_id not in habits_data:
            habits_data[user_id] = []
        
        # Парсим текст привычки (название - описание)
        if " - " in habit_text:
            name, description = habit_text.split(" - ", 1)
        else:
            name = habit_text
            description = "Описание не указано"
        
        # Создаем объект привычки
        habit = {
            "name": name.strip(),
            "description": description.strip(),
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "image_path": image_path
        }
        
        # Добавляем привычку
        habits_data[user_id].append(habit)
        
        # Сохраняем в файл
        with open("data/habits.json", "w", encoding="utf-8") as f:
            json.dump(habits_data, f, ensure_ascii=False, indent=2)
        
    except Exception as e:
        await message.answer(f"Ошибка при сохранении привычки: {e}")
