"""
Модуль для работы с напоминаниями
"""
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import asyncio
from aiogram import Bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


class ReminderService:
    """Сервис для управления напоминаниями"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.active_reminders = {}
        self.reminder_tasks = {}
    
    async def schedule_reminder(self, user_id: int, habit_name: str, 
                              reminder_time: datetime, habit_id: str = None):
        """
        Планирует напоминание о привычке
        """
        reminder_id = f"{user_id}_{habit_id}_{reminder_time.timestamp()}"
        
        # Вычисляем задержку до напоминания
        delay = (reminder_time - datetime.now()).total_seconds()
        
        if delay <= 0:
            # Напоминание уже просрочено
            return False
        
        # Создаем задачу напоминания
        task = asyncio.create_task(
            self._send_reminder(user_id, habit_name, habit_id, delay)
        )
        
        self.reminder_tasks[reminder_id] = task
        self.active_reminders[reminder_id] = {
            'user_id': user_id,
            'habit_name': habit_name,
            'habit_id': habit_id,
            'reminder_time': reminder_time
        }
        
        return True
    
    async def _send_reminder(self, user_id: int, habit_name: str, 
                           habit_id: str, delay: float):
        """
        Отправляет напоминание пользователю
        """
        try:
            # Ждем до времени напоминания
            await asyncio.sleep(delay)
            
            # Создаем клавиатуру для быстрого ответа
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="✅ Выполнено", 
                            callback_data=f"reminder_done_{habit_id}"
                        ),
                        InlineKeyboardButton(
                            text="⏰ Напомнить позже", 
                            callback_data=f"reminder_later_{habit_id}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="❌ Пропустить", 
                            callback_data=f"reminder_skip_{habit_id}"
                        )
                    ]
                ]
            )
            
            reminder_text = (
                f"⏰ Напоминание о привычке\n\n"
                f"📝 {habit_name}\n\n"
                f"Время выполнить привычку! 💪"
            )
            
            await self.bot.send_message(
                chat_id=user_id,
                text=reminder_text,
                reply_markup=keyboard
            )
            
        except Exception as e:
            print(f"Ошибка при отправке напоминания: {e}")
        finally:
            # Удаляем задачу из активных
            reminder_id = f"{user_id}_{habit_id}_{datetime.now().timestamp()}"
            self.reminder_tasks.pop(reminder_id, None)
            self.active_reminders.pop(reminder_id, None)
    
    def cancel_reminder(self, user_id: int, habit_id: str):
        """
        Отменяет напоминание
        """
        # Находим и отменяем задачу
        for reminder_id, task in self.reminder_tasks.items():
            if (reminder_id.startswith(f"{user_id}_{habit_id}") and 
                not task.done()):
                task.cancel()
                del self.reminder_tasks[reminder_id]
                del self.active_reminders[reminder_id]
                return True
        
        return False
    
    def get_user_reminders(self, user_id: int) -> List[Dict]:
        """
        Получает список активных напоминаний пользователя
        """
        user_reminders = []
        for reminder_id, reminder_data in self.active_reminders.items():
            if reminder_data['user_id'] == user_id:
                user_reminders.append({
                    'reminder_id': reminder_id,
                    **reminder_data
                })
        
        return user_reminders
    
    def cancel_all_user_reminders(self, user_id: int):
        """
        Отменяет все напоминания пользователя
        """
        cancelled_count = 0
        for reminder_id, task in list(self.reminder_tasks.items()):
            if (reminder_id.startswith(f"{user_id}_") and not task.done()):
                task.cancel()
                del self.reminder_tasks[reminder_id]
                del self.active_reminders[reminder_id]
                cancelled_count += 1
        
        return cancelled_count
    
    async def schedule_daily_reminders(self, user_id: int, habits: List[Dict]):
        """
        Планирует ежедневные напоминания для всех привычек пользователя
        """
        current_time = datetime.now()
        
        for habit in habits:
            if not habit.get('reminder_enabled', False):
                continue
            
            # Получаем время напоминания
            reminder_time = self._get_reminder_time(habit, current_time)
            if reminder_time:
                await self.schedule_reminder(
                    user_id=user_id,
                    habit_name=habit['name'],
                    reminder_time=reminder_time,
                    habit_id=habit.get('id', 'unknown')
                )
    
    def _get_reminder_time(self, habit: Dict, current_time: datetime) -> Optional[datetime]:
        """
        Вычисляет время следующего напоминания для привычки
        """
        if not habit.get('reminder_time'):
            return None
        
        reminder_time = habit['reminder_time']
        
        # Если время уже прошло сегодня, планируем на завтра
        if reminder_time <= current_time:
            return reminder_time + timedelta(days=1)
        
        return reminder_time
    
    def get_reminder_stats(self, user_id: int) -> Dict:
        """
        Получает статистику напоминаний пользователя
        """
        user_reminders = self.get_user_reminders(user_id)
        
        return {
            'active_reminders': len(user_reminders),
            'total_reminders': len(self.active_reminders),
            'user_reminders': user_reminders
        }


# Глобальная переменная для сервиса напоминаний
reminder_service = None

def init_reminder_service(bot: Bot):
    """Инициализирует сервис напоминаний"""
    global reminder_service
    reminder_service = ReminderService(bot)
    return reminder_service

def get_reminder_service() -> Optional[ReminderService]:
    """Получает экземпляр сервиса напоминаний"""
    return reminder_service
