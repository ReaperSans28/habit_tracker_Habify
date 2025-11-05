"""Пример коллбека напишите что нужно подправить бд подключу в самом конце"""
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import datetime
import keyboards.main_menu as kbmenu
import keyboards.inline as kb
import database.database as db

habit_callback = Router()


class Habit(StatesGroup):
    name_habit = State()
    choose_type = State()
    description1 = State()
    description2 = State()
    habit_day = State()
    habit_days = State()
    time = State()
    time1 = State()


# Обработчик возврата
@habit_callback.callback_query(F.data == "back")
async def back_menu(callback: CallbackQuery):
    await callback.message.answer("Вы вернулись назад", reply_markup=kbmenu.start())
    return

# Начало создания привычки
@habit_callback.callback_query(F.data == "create_habit")
async def create_habit(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Habit.name_habit)
    await callback.message.answer("Введите название вашей привычки ниже ⬇️")


# Получаем название привычки
@habit_callback.message(Habit.name_habit)
async def name_state(message: Message, state: FSMContext):
    await state.update_data(name_habit=message.text)
    await state.set_state(Habit.choose_type)
    await message.answer("Выберите как будете выполнять привычку ⬇️", reply_markup=kb.habit())


# Если выбрал конкретный день
@habit_callback.callback_query(F.data == "habit_day")
async def habit_day_choice(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Habit.habit_day)
    await callback.message.answer("Введите день недели ⬇️")


# Если выбрал несколько дней
@habit_callback.callback_query(F.data == "habit_days")
async def habit_days_choice(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Habit.habit_days)
    await callback.message.answer("Введите дни недели через запятую ⬇️")


# Обработка одного дня
@habit_callback.message(Habit.habit_day)
async def one_day_chosen(message: Message, state: FSMContext):
    await state.update_data(choose_type=message.text)
    await state.set_state(Habit.time)
    await message.answer(f"Введите день недели и время: ")

# Обработка нескольких дней
@habit_callback.message(Habit.habit_days)
async def multiple_days_chosen(message: Message, state: FSMContext):
    await state.update_data(choose_type=message.text)
    await state.set_state(Habit.time)
    await message.answer(f"Введите дни недели и время: ")
    
@habit_callback.message(Habit.time)
async def time_statee(message: Message, state: FSMContext):
    await state.update_data(habit_day=message.text)
    await state.set_state(Habit.description1)
    await message.answer(f"Введите описание вашей привычки: ")
    
@habit_callback.message(Habit.time1)
async def time_state(message: Message, state: FSMContext):
    await state.update_data(habit_days=message.text)
    await state.set_state(Habit.description2)
    await message.answer(f"Введите описание вашей привычки: ")

@habit_callback.message(Habit.description1)
async def descr_state(message: Message, state: FSMContext):
    await state.update_data(time=message.text)
    telegram_id = message.from_user.id
    data = await state.get_data()
    name = data["name_habit"]
    descript = data["description1"]
    created_ad = datetime.datetime.now()
    
    await message.answer(f"Ваша привычка {name} успешно сохранена!")
    db.add_habit(telegram_id, name, descript, created_ad, True, data["time"], 0, 0, 0)
    await state.clear()
    
@habit_callback.message(Habit.description2)
async def descr2_state(message: Message, state: FSMContext):
    await state.update_data(time1=message.text)
    telegram_id = message.from_user.id
    data = await state.get_data()
    name = data["name_habit"]
    descript = data["description2"]
    created_ad = datetime.datetime.now()
    
    await message.answer(f"Ваша привычка {name} успешно сохранена!")
    db.add_habit(telegram_id, name, descript, created_ad, True, data["time1"], 0, 0, 0)
    await state.clear()