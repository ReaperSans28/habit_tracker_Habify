import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import commands_router
from database.database import initialize_database

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в переменных окружения!")
    
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Регистрация роутеров
dp.include_router(commands_router)

async def main():
    # Запуск бота
    logger.info("Запуск бота...")
    initialize_database()
    
    try:
        logger.info("Бот успешно запущен!")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Произошла ошибка при запуске бота: {e}")
        return 1
    finally:
        logger.info("Завершение работы бота...")
        await bot.session.close()
        
    return 0


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Необработанная ошибка: {e}")
        sys.exit(1)

