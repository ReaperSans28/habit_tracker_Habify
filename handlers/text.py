"""
Обработчики текстовых сообщений
"""
from aiogram import Router, F
from aiogram.types import Message
from utils.text_parser import text_parser
from utils.date_parser import date_parser

# Создаем роутер для текстовых сообщений
text_router = Router()


@text_router.message(F.text == "📊 Мои привычки")
async def show_habits(message: Message):
    """Показать список привычек пользователя"""
    await message.answer(
        "📊 Ваши привычки:\n\n"
        "Пока что у вас нет добавленных привычек.\n"
        "Используйте кнопку '➕ Добавить привычку' для создания новой привычки."
    )


@text_router.message(F.text == "➕ Добавить привычку")
async def add_habit_start(message: Message):
    """Начать процесс добавления привычки"""
    await message.answer(
        "➕ Добавление новой привычки\n\n"
        "Напишите название привычки, которую хотите отслеживать.\n\n"
        "Например: 'Читать 30 минут в день' или 'Делать зарядку'"
    )


@text_router.message(F.text == "📈 Статистика")
async def show_statistics(message: Message):
    """Показать статистику привычек"""
    await message.answer(
        "📈 Статистика привычек\n\n"
        "Пока что статистика недоступна.\n"
        "Добавьте привычки и начните их отслеживать!"
    )


@text_router.message(F.text == "⚙️ Настройки")
async def show_settings(message: Message):
    """Показать настройки"""
    await message.answer(
        "⚙️ Настройки\n\n"
        "Здесь будут настройки бота.\n"
        "Функция в разработке."
    )


@text_router.message(F.text == "❓ Помощь")
async def show_help(message: Message):
    """Показать помощь"""
    await message.answer(
        "❓ Помощь\n\n"
        "Этот бот поможет вам отслеживать привычки.\n\n"
        "Основные функции:\n"
        "• Добавление новых привычек\n"
        "• Отметка выполнения привычек\n"
        "• Просмотр статистики\n"
        "• Парсинг дат и времени\n"
        "• Напоминания о привычках\n\n"
        "Используйте кнопки меню для навигации."
    )


@text_router.message(F.text.startswith("📅"))
async def handle_date_parsing(message: Message):
    """Обработчик для парсинга дат"""
    text = message.text[2:].strip()  # Убираем эмодзи
    
    if not text:
        await message.answer("❌ Отправьте дату для парсинга")
        return
    
    # Парсим дату
    parsed_date = date_parser.parse_date(text)
    
    if parsed_date:
        is_valid, error = date_parser.validate_date(parsed_date)
        
        if is_valid:
            formatted_date = date_parser.format_date(parsed_date)
            relative_date = date_parser.get_relative_date(parsed_date)
            
            response_text = (
                f"📅 Дата распознана!\n\n"
                f"📆 Формат: {formatted_date}\n"
                f"📝 Относительно: {relative_date}\n"
                f"⏰ Время: {parsed_date.strftime('%H:%M')}"
            )
        else:
            response_text = f"❌ Ошибка валидации: {error}"
    else:
        response_text = (
            "❌ Не удалось распознать дату\n\n"
            "Попробуйте форматы:\n"
            "• Сегодня, завтра, вчера\n"
            "• 25.12.2024\n"
            "• Понедельник\n"
            "• Через 3 дня"
        )
    
    await message.answer(response_text)


# Обработчик для добавления привычки через текст
@text_router.message()
async def handle_habit_text(message: Message):
    """Обработчик для текста привычки с парсингом данных"""
    # Простая валидация длины
    if len(message.text) < 3:
        await message.answer("❌ Название привычки слишком короткое. Попробуйте еще раз.")
        return
    
    if len(message.text) > 200:
        await message.answer("❌ Название привычки слишком длинное. Максимум 200 символов.")
        return
    
    # Парсим текст привычки
    parsed_data = text_parser.parse_habit_text(message.text)
    
    # Формируем ответ с извлеченной информацией
    response_parts = [f"✅ Привычка добавлена!\n\n📝 Название: {parsed_data['name']}"]
    
    # Добавляем информацию о частоте
    if parsed_data['frequency']:
        freq = parsed_data['frequency']
        if freq['type'] == 'daily':
            if freq['interval'] == 1:
                response_parts.append("🔄 Частота: каждый день")
            else:
                response_parts.append(f"🔄 Частота: каждые {freq['interval']} дней")
        elif freq['type'] == 'weekly':
            if freq['interval'] == 1:
                response_parts.append("🔄 Частота: каждую неделю")
            else:
                response_parts.append(f"🔄 Частота: каждые {freq['interval']} недель")
        elif freq['type'] == 'monthly':
            if freq['interval'] == 1:
                response_parts.append("🔄 Частота: каждый месяц")
            else:
                response_parts.append(f"🔄 Частота: каждые {freq['interval']} месяцев")
    
    # Добавляем информацию о времени
    if parsed_data['time']:
        time_info = parsed_data['time']
        time_str = f"{time_info['hour']:02d}:{time_info['minute']:02d}"
        response_parts.append(f"⏰ Время: {time_str}")
    
    # Добавляем информацию о продолжительности
    if parsed_data['duration']:
        duration = parsed_data['duration']
        if duration['unit'] == 'minutes':
            response_parts.append(f"⏱️ Продолжительность: {duration['value']} мин.")
        elif duration['unit'] == 'hours':
            response_parts.append(f"⏱️ Продолжительность: {duration['value']} ч.")
    
    # Добавляем информацию о датах
    if parsed_data['dates']:
        dates_str = ", ".join([date_parser.format_date(date) for date in parsed_data['dates']])
        response_parts.append(f"📅 Даты: {dates_str}")
    
    # Добавляем информацию о напоминаниях
    if parsed_data['reminder']:
        response_parts.append("🔔 Напоминания включены")
    
    # Добавляем ошибки, если есть
    if parsed_data['errors']:
        response_parts.append(f"\n⚠️ Ошибки: {', '.join(parsed_data['errors'])}")
    
    response_text = "\n".join(response_parts)
    await message.answer(response_text)
