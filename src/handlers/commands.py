from aiogram.types import Message
from aiogram.filters import Command
from aiogram import Router

commands_router = Router()

@commands_router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды start"""
    welcome_text = (
        f"Привет, {message.from_user.first_name}.\n"
        f"Я бот для трекинга твоих привычек\n"
        f"Если нужна помощь -> /help"
    )
    await message.answer(welcome_text)


@commands_router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды help"""
    welcome_text = (
        f"Команды бота:\n"
        f"/start - запуск / перезагрузка бота"
    )
    await message.answer(welcome_text)
