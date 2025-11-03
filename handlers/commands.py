from aiogram.types import Message
from aiogram.filters import Command
from aiogram import Router

import database.database as db
import keyboards.inline as kb
import keyboards.main_menu as menu

commands_router = Router()

from handlers.messages import render_message
from utils.name_validator import validate_name, NameValidationResult, Gender

# +++ НОВОЕ: FSM для сбора имени
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

class Onboarding(StatesGroup):
    waiting_for_name = State()

import asyncio

@commands_router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    users_telegram_id = (message.from_user.id if message.from_user else None)
    if not users_telegram_id:
        raise ValueError("Не удалось получить telegram_id пользователя.")

    # пытаемся получить пользователя из БД
    user = db.get_user(users_telegram_id)

    # === Новый пользователь ===================================================
    if not user:
        # новый пользователь, валидируем имя
        users_first_name = (message.from_user.first_name 
                            if message.from_user and message.from_user.first_name else "")
        nvr: NameValidationResult = validate_name(users_first_name)
        if not nvr.is_valid:
            # Нет валидного имени — просим корректное
            await message.answer(
                render_message("ask_name", username="", gender="unknown"),
                reply_markup=None,
            )
            await state.set_state(Onboarding.waiting_for_name)
            return
        
        # Имя валидно — создаём пользователя и показываем онбординг (пока привычек нет)
        users_gender: Gender = nvr.gender
        name_normalized = users_first_name[:1].upper() + users_first_name[1:]    # нормализация капитализации

        # Создаём запись в БД
        db.add_user(users_telegram_id, name_normalized, users_gender, True)

        # Приветственное сообщение Wednesday (из start_new)
        await message.answer(render_message("start_new", name_normalized, users_gender))
        await asyncio.sleep(1.2)

        # Далее — онбординг (нет привычек → одна кнопка)
        await message.answer(
            render_message("onboarding_intro", name_normalized, users_gender),
            reply_markup=menu.onboarding()
        )

        return

    # === Существующий пользователь ============================================

    # Существующий пользователь — приветствуем
    users_first_name = user["first_name"]
    users_gender = user["gender"]
    await message.answer(
        render_message("start_existing", users_first_name, users_gender)
    )

    # Проверить список активных привычек
    active_habits = db.get_active_habits(users_telegram_id)
    if active_habits.empty:
        # Нет привычек — онбординг
        await asyncio.sleep(1.2)
        await message.answer(
            render_message("onboarding_intro", users_first_name, users_gender),
            reply_markup=menu.onboarding()
        )
    
    else:
        # Есть привычки — показать главное меню
        await asyncio.sleep(1.2)
        await message.answer(
            "Главное меню:",
            reply_markup=menu.start()
        )


# === Приём имени в состоянии ожидания ========================================
@commands_router.message(Onboarding.waiting_for_name)
async def handle_name_input(message: Message, state: FSMContext):
    incoming = (message.text or "").strip()
    nvr: NameValidationResult = validate_name(incoming)

    if not nvr.is_valid:
        reason_map = {
            "Имя отсутствует": "имя отсутствует",
            "Имя слишком короткое": "слишком короткое имя",
            "Имя содержит недопустимые символы": "лишние символы",
        }
        reason = reason_map.get(nvr.reason_invalid or "", nvr.reason_invalid or "ошибка формата")
        await message.answer(render_message("name_invalid_retry", username="", gender="unknown", 
                                            reason=reason))
        return

    # Валидно — сохраняем, приветствуем
    users_telegram_id = (message.from_user.id if message.from_user else None)
    if not users_telegram_id:
        raise ValueError("Не удалось получить telegram_id пользователя.") # на всякий случай
    users_gender: Gender = nvr.gender
    name_normalized = incoming[:1].upper() + incoming[1:]

    db.add_user(users_telegram_id, name_normalized, users_gender, True)
    await state.clear()

    # Приветственное сообщение Wednesday (из start_new)
    await message.answer(render_message("start_new", name_normalized, users_gender))
    await asyncio.sleep(1.2)
    # Далее — онбординг (нет привычек → одна кнопка)
    await message.answer(
        render_message("onboarding_intro", name_normalized, users_gender),
        reply_markup=menu.onboarding()
    )
    return



# @commands_router.message(Command("my_habits"))
# async def habits_cmd(message: Message):
#     await message.answer("📦 Ваш список привычек ⬇️:", reply_markup=kb.my_habits)
#     return

