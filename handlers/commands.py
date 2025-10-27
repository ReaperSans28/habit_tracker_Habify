"""
Обработчики команд бота
"""
from aiogram import Router, F, types
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import requests
import random
from bs4 import BeautifulSoup
import keyboards.inline as kb
import database.database as db
from config import QUOTES_URL


commands_router = Router()

# ==============================
# FSM состояния для добавления привычки
# ==============================
class AddHabit(StatesGroup):
    name = State()
    description = State()


# ==============================
# /start
# ==============================
@commands_router.message(Command("start"))
async def cmd_start(message: Message):
    telegram_id = message.from_user.id
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""

    # Добавляем пользователя в БД
    user_id = db.add_user_if_not_exists(telegram_id, username, first_name, last_name)

    habits = db.get_habits(user_id)

    if not habits:
        await message.answer(
            f"👋 Привет, {first_name}!\n\n"
            "У тебя пока нет привычек.\n"
            "Добавь первую привычку командой /addhabbit 💪"
        )
    else:
        habit_id = habits[0][0]
        habit_name = habits[0][2]
        await message.answer(
            f"👋 Привет, {first_name}!\n\n"
            f"Твоя привычка: {habit_name}\n"
            "Ты можешь отмечать выполнение ниже 👇",
            reply_markup=kb.get_habit_actions_keyboard(habit_id)
        )


# ==============================
# /add — добавление новой привычки
# ==============================
@commands_router.message(Command("addhabbit"))
async def cmd_add(message: Message, state: FSMContext):
    telegram_id = message.from_user.id
    username = message.from_user.username or ""
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""
    user_id = db.add_user_if_not_exists(telegram_id, username, first_name, last_name)
    habits = db.get_habits(user_id)

    await message.answer("📝 Здесь ты можешь добавить свою привычку:", reply_markup=kb.get_habit_list_keyboard(habits))


# ==============================
# Обработчики кнопок привычек
# ==============================
@commands_router.callback_query(F.data.startswith("mark_done_"))
async def mark_done(callback: CallbackQuery):
    habit_id = int(callback.data.split("_")[2])
    db.mark_habit(habit_id, "done")
    await callback.answer("✅ Привычка отмечена как выполненная!")


@commands_router.callback_query(F.data.startswith("delete_habit_"))
async def delete_habit(callback: CallbackQuery):
    habit_id = int(callback.data.split("_")[2])
    db.delete_habit(habit_id)
    await callback.message.edit_text("🗑 Привычка удалена.")


@commands_router.callback_query(F.data.startswith("stats_"))
async def stats(callback: CallbackQuery):
    habit_id = int(callback.data.split("_")[1])
    count = db.get_habit_stats(habit_id)
    await callback.answer(f"📊 Выполнено {count} раз!", show_alert=True)


# ==============================
# /help — помощь
# ==============================
@commands_router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "📋 Команды:\n\n"
        "/start — Начать работу\n"
        "/addhabbit — Добавить новую привычку\n"
        "/help — Список команд\n"
        "/quotes — Мотивационные цитаты 💬\n"
        "/myhabits — Мои привычки"
    )
    

# ==============================
# /my_habits — посмотреть все свои привычки
# ==============================
@commands_router.message(Command("myhabits"))
async def show_user_habits(message: types.Message):
    """Показывает список всех текущих привычек пользователя"""
    telegram_id = message.from_user.id
    user = db.get_user(telegram_id)
    
    if not user:
        await message.answer("❌ Пользователь не найден. Используй /start.")
        return
    
    user_id = user[0]
    habits = db.get_habits(user_id)  # предполагается, что возвращает [(id, name), ...]
    
    if not habits:
        await message.answer("У тебя пока нет привычек. Добавь новую с помощью /add_habit")
        return
    
    # Получаем список названий привычек
    habit_names = [h[1] for h in habits]

    # Создаём клавиатуру со всеми привычками
    keyboard = kb.get_habit_list_keyboard(habit_names)

    await message.answer("Вот твои текущие привычки:", reply_markup=keyboard)


# ==============================
# /quotes — цитаты
# ==============================
@commands_router.message(Command("quotes"))
async def cmd_quote(message: Message):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(QUOTES_URL, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        quotes = soup.find_all('div', class_='field-name-body')

        quote_texts = []
        for quote in quotes:
            for p in quote.find_all('p'):
                text = p.get_text(strip=True)
                if len(text) > 10:
                    quote_texts.append(text)

        if not quote_texts:
            await message.answer("Цитаты не найдены 😞")
            return

        random_quote = random.choice(quote_texts)
        await message.answer(f"💬 {random_quote}")

    except Exception as e:
        await message.answer("⚠️ Ошибка при загрузке цитат.")
        print(e)