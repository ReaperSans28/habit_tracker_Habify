# messages.py
from dataclasses import dataclass
from typing import Dict, List, Literal
import random

from utils.name_validator import Gender


@dataclass(frozen=True)
class Message:
    id: str
    text: str  

def gender_tokens(gender: Gender) -> Dict[str, str]:
    """Набор словоформ под пол. Нейтральные — без корявых '(а)'."""
    if gender == "male":
        return {
            "decided": "решил",
            "Decided": "Решил",
            "ready": "готов",
            "Ready": "Готов",
            "returned": "вернулся",
        }
    if gender == "female":
        return {
            "decided": "решила",
            "Decided": "Решила",
            "ready": "готова",
            "Ready": "Готова",
            "returned": "вернулась",
        }
    # unknown
    return {
        "decided": "решил",
        "Decided": "Решил",
        "ready": "готов",
        "Ready": "Готов",
        "returned": "снова здесь",  # нейтрально и естественно
    }

CATALOG: Dict[str, List[Message]] = {
    # Первое появление (согласовано с About — «фиксация, без мотивации»)
    "start_new": [
        Message("sn1",
            "Привет, {username}. Похвально, что ты {decided} начать. Я — наблюдаю."),
        Message("sn2",
            "Добро пожаловать, {username}. {ready} фиксировать свои привычки? Без мотивации, только цифры."),
        Message("sn3",
            "{username}, отмечаю твоё появление. Посмотрим, сколько продержится энтузиазм."),
        Message("sn4",
            "Начнём, {username}. Ещё одна попытка укротить хаос. У меня — хронометр."),
        Message("sn5",
            "Отлично, {username}. {Decided} поверить в дисциплину? Я сохраню доказательства."),
        Message("sn6",
            "**безэмоционально** Пользователь {username} активирован. Фиксация начата."),
    ],

    # Повторный визит (пользователь уже есть)
    "start_existing": [
        Message("se1",
            "Снова ты, {username}. Значит, ты {returned}. Продолжим фиксацию."),
        Message("se2",
            "Wednesday отмечает возвращение пользователя {username}. Как продвигается борьба с собой?"),
        Message("se3",
            "О, {username} вернулся. Привычки ещё ждут. Некоторые — уже смирились с забвением."),
        Message("se4",
            "**холодно** {username}, журнал открыт. Готов обновить статистику провалов… и редких успехов?"),
        Message("se5",
            "Каждое возвращение — маленький подвиг. Или просто очередная попытка. Что скажешь, {username}?"),
    ],
}

# Дополняем каталог сообщениями для запроса и валидации имени
CATALOG.update({
    "ask_name": [
        Message("an1", "Как мне к тебе обращаться? Только имя. Без героических титулов."),
        Message("an2", "Нужно имя. Коротко и без спецсимволов. Я не коллекционирую ники."),
        Message("an3", "**безэмоционально** Введи имя. Остальное я вычислю сама."),
    ],
    "name_invalid_retry": [
        Message("nr1", "Это не похоже на имя: {reason}. Попробуй ещё раз, без цифр и лишних символов."),
        Message("nr2", "Промах. {reason}. Дай нормальное имя, я не придираюсь — я фильтрую шум."),
        Message("nr3", "Имя не принято ({reason}). Ещё попытка."),
    ],
})

# Онбординг — когда нет привычек
CATALOG.update({
    "onboarding_intro": [
        Message("ob1", "Начнём с очевидного. У тебя нет привычек. Пока что."),
        Message("ob2", "Пока тут пусто. Это даже удобно — не придётся удалять провалы."),
        Message("ob3", "**монотонно** Ноль привычек. Идеальная статистика. Исправим?"),
    ],
})

from utils.name_validator import Gender

def render_message(key: str, username: str, gender: Gender, **extra) -> str:
    """Возвращает случайный текст из каталога, подставляя имя, пол и доп. токены."""
    msg = random.choice(CATALOG[key])
    tokens = {"username": username, **gender_tokens(gender), **extra}
    return msg.text.format(**tokens)

