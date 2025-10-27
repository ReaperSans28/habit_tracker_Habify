import os
from datetime import datetime
from aiogram.types import Message
from aiogram import Router
from aiogram.fsm.context import FSMContext
from .commands import HabitStates
from .text import save_habit_to_json

media_router = Router()

@media_router.message(HabitStates.waiting_for_habit_image)
async def process_habit_image(message: Message, state: FSMContext):
    """Обработка изображения для привычки"""
    if not message.photo:
        await message.answer("Пожалуйста, отправьте изображение или напишите 'пропустить'.")
        return
    
    try:
        # Получаем данные из состояния
        data = await state.get_data()
        habit_text = data['habit_text']
        
        # Создаем уникальное имя файла
        user_id = message.from_user.id
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"habit_{user_id}_{timestamp}.jpg"
        
        # Путь для сохранения изображения
        image_path = f"data/habit_images/{filename}"
        
        # Скачиваем изображение
        photo = message.photo[-1]  # Берем самое большое разрешение
        file_info = await message.bot.get_file(photo.file_id)
        
        # Создаем директорию если не существует
        os.makedirs("data/habit_images", exist_ok=True)
        
        # Сохраняем файл
        await message.bot.download_file(file_info.file_path, image_path)
        
        # Сохраняем привычку с изображением
        await save_habit_to_json(message, habit_text, image_path)
        
        # Очищаем состояние
        await state.clear()
        
        await message.answer(
            f"Отлично! Привычка '{habit_text}' успешно добавлена с изображением! 📷"
        )
        
    except Exception as e:
        await message.answer(f"Ошибка при обработке изображения: {e}")
        await state.clear()
