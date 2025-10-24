import asyncio

from config import BOT_TOKEN
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from src.handlers import commands, text, media

async def main():
    """Запуск."""
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(commands.commands_router)
    dp.include_router(text.text_router)
    dp.include_router(media.media_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот приостановлен")
    except Exception as e:
        print(f"Ошибка: {e}")
