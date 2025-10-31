from aiogram.types import Message
from aiogram.filters import Command
from aiogram import Router
import random

import database.database as db

commands_router = Router()

start_new_message_options = [
    (
        "Привет! Я - Wednesday. Голос ценичного порядка в твоей бесплодной борьбе за "
        "продуктивность. Я не вдохновляю - я фиксирую крах. Чем могу быть полезна?"
    ),
    (
        "А, новая жертва самосовершенствования. Я Wednesday, и я буду вести учет твоих "
        "попыток изменить жизнь. Спойлер: обычно все заканчивается разочарованием."
    ),
    (
        "Приветствую в черной комедии под названием 'Самосовершенствование'. Я Wednesday, "
        "твой верный хронист неудач и редких, случайных достижений."
    ),
    (
        "**монотонно** Wednesday слушает. Давай начнем наше увлекательное путешествие "
        "по спирали бесконечных попыток стать лучше. Я уже в предвкушении."

    )

]

start_existing_message_options = [
    (
        "Снова ты? Ну что ж, продолжим фиксировать твои попытки стать лучше. "
        "Помни, я здесь, чтобы напоминать тебе о реальности."
    ),
    (
        "О, ты вернулся. Надеюсь, на этот раз у тебя есть хоть какие-то успехи, "
        "чтобы я могла записать их в свою мрачную хронику."
    ),
    (
        "Снова здравствуй. Готова продолжать наше путешествие по бескрайним просторам "
        "самосовершенствования? Я уже приготовила свои саркастические заметки."
    ),
    (
        "**монотонно** Ты снова здесь. Давай посмотрим, сколько раз ты смог "
        "провалиться или, может быть, даже добиться чего-то стоящего."
    )
]



@commands_router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    user = db.get_user(user_id)

    pass

    if user:
        await message.answer(random.choice(start_new_message_options))
        return
    else:
        await message.answer(random.choice(start_existing_message_options))
        db.add_user(user_id)
        return