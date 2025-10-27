"""
Основной файл бота-трекера привычек
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

# Загружаем нашу базу данных
from database.database import init_db

# Импорты роутеров
from handlers.commands import commands_router
from handlers.text import text_router
from handlers.media import media_router
from handlers.callbacks import callback_router
    
# Импорты конфигурации
from config import BOT_TOKEN

# Диспетчер нужен для запуска бота
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Импорты утилит
from utils.reminder_service import init_reminder_service

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
# Загружаем нашу базу данных
init_db()

async def main():
    """Основная функция запуска бота"""
    # Создаем экземпляры бота и диспетчера
    
    # Инициализируем сервис напоминаний
    reminder_service = init_reminder_service(bot)
    logger.info("Сервис напоминаний инициализирован")
    
    # Регистрируем роутеры
    dp.include_router(commands_router)
    dp.include_router(callback_router)
    
    logger.info("Бот запущен!")
    
    try:
        # Запускаем бота
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Критическая ошибка: {e}")
