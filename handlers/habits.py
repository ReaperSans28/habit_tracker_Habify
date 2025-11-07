# handlers/habits.py
from aiogram import F, Router
from aiogram.types import CallbackQuery
from keyboards import main_menu as menu
import database.database as db

habits_router = Router()

# Домой (главное меню)
@habits_router.callback_query(F.data == "home")
async def go_home(callback: CallbackQuery):
    uid = callback.from_user.id
    reply = menu.home(
        today_count=getattr(db, "count_due_today", lambda _uid: 0)(uid),
        has_habits=getattr(db, "count_habits", lambda _uid: 0)(uid) > 0,
        has_active=getattr(db, "count_active_habits", lambda _uid: 0)(uid) > 0,
        has_inactive=getattr(db, "count_inactive_habits", lambda _uid: 0)(uid) > 0,
    )
    await callback.message.edit_reply_markup(reply_markup=reply)
    await callback.answer()

# Список привычек (пагинация)
@habits_router.callback_query(F.data.startswith("habit:list:page:"))
async def list_habits_cb(callback: CallbackQuery):
    uid = callback.from_user.id
    # формат: habit:list:page:<n>
    page = int(callback.data.split(":")[-1])
    page_size = 6

    # ожидаемый формат данных из БД: [(id, name, is_active, reminder_str), ...], total
    items, total = db.list_habits(uid, page=page, page_size=page_size)
    reply = menu.list_habits(items, page=page, page_size=page_size, total_count=total)

    await callback.message.edit_reply_markup(reply_markup=reply)
    await callback.answer()

# Открыть карточку
@habits_router.callback_query(F.data.startswith("habit:open:"))
async def open_habit(cb: CallbackQuery):
    hid = int(cb.data.split(":")[-1])
    h = db.get_habit(hid)
    reply = menu.habit_actions(
        habit_id=h["habit_id"],
        name=h["name"],
        is_active=bool(int(h["is_active"])) if isinstance(h["is_active"], str) else bool(h["is_active"]),
    )
    await cb.message.edit_reply_markup(reply_markup=reply)
    await cb.answer()

# Отметить выполнено
@habits_router.callback_query(F.data.startswith("habit:check:"))
async def check_habit(cb: CallbackQuery):
    hid = int(cb.data.split(":")[-1])
    db.mark_habit_done(cb.from_user.id, hid)  # реализуй в БД (добавь запись "done today")
    await cb.answer("Зафиксировано.")

# Вкл/выкл
@habits_router.callback_query(F.data.startswith("habit:deactivate:"))
async def deactivate_habit(cb: CallbackQuery):
    hid = int(cb.data.split(":")[-1])
    db.set_habit_active(hid, False)
    await open_habit(cb)

@habits_router.callback_query(F.data.startswith("habit:activate:"))
async def activate_habit(cb: CallbackQuery):
    hid = int(cb.data.split(":")[-1])
    db.set_habit_active(hid, True)
    await open_habit(cb)

# Переименовать / Расписание / Напоминание — заглушки под твои FSM/диалоги
@habits_router.callback_query(F.data.startswith("habit:rename:"))
async def rename_habit_start(cb: CallbackQuery):
    await cb.answer("Переименование: пока заглушка.")

@habits_router.callback_query(F.data.startswith("habit:schedule:"))
async def schedule_habit_start(cb: CallbackQuery):
    await cb.answer("Расписание: пока заглушка.")

@habits_router.callback_query(F.data.startswith("habit:reminder:"))
async def reminder_habit_start(cb: CallbackQuery):
    await cb.answer("Напоминание: пока заглушка.")

# Удаление
@habits_router.callback_query(F.data.startswith("habit:delete_confirm:"))
async def delete_confirm(cb: CallbackQuery):
    hid = int(cb.data.split(":")[-1])
    h = db.get_habit(hid)
    await cb.message.edit_reply_markup(reply_markup=menu.confirm_delete(hid, h["name"]))
    await cb.answer()

@habits_router.callback_query(F.data.startswith("habit:delete:"))
async def delete_habit(cb: CallbackQuery):
    hid = int(cb.data.split(":")[-1])
    db.delete_habit(hid)
    # после удаления — на список (первая страница)
    uid = cb.from_user.id
    items, total = db.list_habits(uid, page=1, page_size=6)
    await cb.message.edit_reply_markup(
        reply_markup=menu.list_habits(items, page=1, page_size=6, total_count=total)
    )
    await cb.answer("Удалено.")
