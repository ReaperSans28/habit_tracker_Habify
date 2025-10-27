"""
Обработчики callback запросов от inline-кнопок
Исправленная версия с корректной обработкой добавления и редактирования привычек
"""
from aiogram import Router, F, types
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from keyboards.inline import get_habit_actions_keyboard, get_confirmation_keyboard, back
import database.database as db

callback_router = Router()

# ==============================
# FSM для добавления и редактирования привычки
# ==============================
class HabitFSM(StatesGroup):
    add_name = State()
    add_description = State()
    edit_name = State()
    edit_description = State()

# ==============================
# Вспомогательная функция для получения ID привычки из callback_data
# ==============================
def parse_habit_id(callback_data: str) -> int | None:
    parts = callback_data.split("_")
    if len(parts) < 3 or not parts[-1].isdigit():
        return None
    return int(parts[-1])

# ==============================
# Добавление новой привычки через кнопку
# ==============================
@callback_router.callback_query(F.data == "add_new_habit")
async def handle_add_new_habit(callback: CallbackQuery, state: FSMContext):
    await state.clear()  # очищаем текущее состояние FSM
    await state.set_state(HabitFSM.add_name)
    await callback.answer()
    await callback.message.edit_text(
        "📝 Введи название новой привычки, которую хочешь отслеживать.\n"
        "Например: 'Читать 30 минут' или 'Пить воду 8 стаканов в день'"
    )

@callback_router.message(HabitFSM.add_name)
async def add_habit_name(message: types.Message, state: FSMContext):
    habit_name = message.text.strip()
    if len(habit_name) < 3:
        await message.answer("❌ Название привычки слишком короткое. Попробуй еще раз.")
        return
    await state.update_data(name=habit_name)
    await state.set_state(HabitFSM.add_description)
    await message.answer("✏️ Введи описание привычки (или напиши `-`, если не нужно):")

@callback_router.message(HabitFSM.add_description)
async def add_habit_description(message: types.Message, state: FSMContext):
    data = await state.get_data()
    habit_name = data["name"]
    description = message.text if message.text != "-" else ""

    telegram_id = message.from_user.id
    user = db.get_user(telegram_id)
    if not user:
        await message.answer("❌ Пользователь не найден. Используй /start.")
        await state.clear()
        return

    user_id = user[0]
    db.add_habit(user_id, habit_name, description)
    habits = db.get_habits(user_id)
    habit_id = habits[-1][0]

    await message.answer(
        f"✅ Привычка '{habit_name}' успешно добавлена!\nТеперь можешь её отслеживать 👇",
        reply_markup=get_habit_actions_keyboard(habit_id)
    )
    await state.clear()

# ==============================
# Редактирование привычки
# ==============================
@callback_router.callback_query(F.data.startswith("habit_edit_"))
async def handle_edit_habit(callback: CallbackQuery, state: FSMContext):
    habit_id = parse_habit_id(callback.data)
    if habit_id is None:
        await callback.answer("Ошибка: некорректный ID привычки.", show_alert=True)
        return
    await state.clear()
    await state.update_data(habit_id=habit_id)
    await state.set_state(HabitFSM.edit_name)
    await callback.answer()
    await callback.message.edit_text("✏️ Введи новое название привычки:")

@callback_router.message(HabitFSM.edit_name)
async def edit_habit_name(message: types.Message, state: FSMContext):
    habit_name = message.text.strip()
    if len(habit_name) < 3:
        await message.answer("❌ Название привычки слишком короткое. Попробуй еще раз.")
        return
    await state.update_data(new_name=habit_name)
    await state.set_state(HabitFSM.edit_description)
    await message.answer("✏️ Введи новое описание привычки (или напиши `-`, если не нужно):")

@callback_router.message(HabitFSM.edit_description)
async def edit_habit_description(message: types.Message, state: FSMContext):
    data = await state.get_data()
    habit_id = data['habit_id']
    new_name = data['new_name']
    new_description = message.text if message.text != "-" else ""

    db.update_habit(habit_id, new_name, new_description)
    await message.answer(f"✅ Привычка обновлена: {new_name}", reply_markup=back())
    await state.clear()

# ==============================
# Отметить выполнение привычки
# ==============================
@callback_router.callback_query(F.data.startswith("habit_done_"))
async def handle_habit_done(callback: CallbackQuery):
    habit_id = parse_habit_id(callback.data)
    if habit_id is None:
        await callback.answer("Ошибка: некорректный ID привычки.", show_alert=True)
        return

    db.mark_habit(habit_id, "done")
    await callback.answer("✅ Привычка выполнена!")

    # Обновляем список привычек
    telegram_id = callback.from_user.id
    user = db.get_user(telegram_id)
    if user:
        user_id = user[0]
        habits = db.get_habits(user_id)
        from keyboards.inline import get_habit_list_keyboard
        if habits:
            await callback.message.edit_text(
                "Вот твои текущие привычки:",
                reply_markup=get_habit_list_keyboard([h[2] for h in habits])
            )
        else:
            await callback.message.edit_text("🎉 Все привычки выполнены!")

# ==============================
# Удаление привычки
# ==============================
@callback_router.callback_query(F.data.startswith("habit_delete_"))
async def handle_habit_delete(callback: CallbackQuery):
    habit_id = parse_habit_id(callback.data)
    if habit_id is None:
        await callback.answer("Ошибка: некорректный ID привычки.", show_alert=True)
        return
    await callback.answer()
    await callback.message.edit_text(
        f"🗑 Вы уверены, что хотите удалить привычку #{habit_id}?",
        reply_markup=get_confirmation_keyboard("delete", habit_id)
    )

@callback_router.callback_query(F.data.startswith("confirm_delete_"))
async def confirm_delete(callback: CallbackQuery):
    habit_id = parse_habit_id(callback.data)
    if habit_id is None:
        await callback.answer("Ошибка: некорректный ID привычки.", show_alert=True)
        return
    db.delete_habit(habit_id)
    await callback.answer("✅ Привычка удалена!")
    await callback.message.edit_text("✅ Привычка успешно удалена.")

@callback_router.callback_query(F.data.startswith("cancel_delete_"))
async def cancel_delete(callback: CallbackQuery):
    habit_id = parse_habit_id(callback.data)
    if habit_id is None:
        await callback.answer("Ошибка: некорректный ID привычки.", show_alert=True)
        return
    await callback.answer("❌ Отмена удаления")
    await callback.message.edit_text(
        f"❌ Удаление привычки #{habit_id} отменено.",
        reply_markup=get_habit_actions_keyboard(habit_id)
    )
    
@callback_router.callback_query(F.data.startswith("select_habit_"))
async def select_habit(callback: CallbackQuery):
    habit_id = int(callback.data.split("_")[-1])  # ID должен быть числом
    habit = db.get_habit_by_id(habit_id)

    if not habit:
        await callback.answer("❌ Привычка не найдена", show_alert=True)
        return

    text = f"📝 Привычка: {habit[2]}"
    if habit[3]:
        text += f"\nОписание: {habit[3]}"

    await callback.message.edit_text(
        text,
        reply_markup=get_habit_actions_keyboard(habit_id)
    )
