"""Пример коллбека напишите что нужно подправить бд подключу в самом конце"""
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import keyboards.inline as kb
import database.database as db

cb = Router()


class Habit(StatesGroup):
    name_habit = State()
    choose_type = State()
    habit_day = State()
    habit_days = State()


# Обработчик возврата
@cb.callback_query(F.data == "back")
async def back_menu(callback: CallbackQuery):
    await callback.message.answer("Вы вернулись назад", reply_markup=kb.start())


# Начало создания привычки
@cb.callback_query(F.data == "create_habit")
async def create_habit(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Habit.name_habit)
    await callback.message.answer("Введите название вашей привычки ниже ⬇️")


# Получаем название привычки
@cb.message(Habit.name_habit)
async def name_state(message: Message, state: FSMContext):
    await state.update_data(name_habit=message.text)
    await state.set_state(Habit.choose_type)
    await message.answer("Выберите как будете выполнять привычку ⬇️", reply_markup=kb.habit())


# Если выбрал конкретный день
@cb.callback_query(F.data == "habit_day")
async def habit_day_choice(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Habit.habit_day)
    await callback.message.answer("Введите день недели ⬇️")


# Если выбрал несколько дней
@cb.callback_query(F.data == "habit_days")
async def habit_days_choice(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Habit.habit_days)
    await callback.message.answer("Введите дни недели через запятую ⬇️")


# Обработка одного дня
@cb.message(Habit.habit_day)
async def one_day_chosen(message: Message, state: FSMContext):
    data = await state.get_data()
    name = data.get("name_habit")

    await state.update_data(habit_day=message.text)
    await message.answer(f"Привычка '{name}' сохранена! День недели: {message.text}")
    await state.clear()


# Обработка нескольких дней
@cb.message(Habit.habit_days)
async def multiple_days_chosen(message: Message, state: FSMContext):
    data = await state.get_data()
    name = data.get("name_habit")

    await state.update_data(habit_days=message.text)
    await message.answer(f"Привычка '{name}' сохранена!\nДни недели: {message.text}")
    await state.clear()