"""
Утилиты для валидации и обработки имени пользователя
"""
import re
from typing import Tuple, Optional, Dict, Set
from dataclasses import dataclass

from typing import Literal
Gender = Literal["male", "female", "unknown"]

# Популярные мужские имена (кириллица и латиница)
MALE_NAMES: Set[str] = {
    # Имена кириллицей
    'александр', 'дмитрий', 'максим', 'сергей', 'андрей', 'алексей', 'артём', 'илья',
    'кирилл', 'михаил', 'никита', 'матвей', 'роман', 'егор', 'арсений', 'иван', 'денис',
    'евгений', 'даниил', 'тимофей', 'владислав', 'игорь', 'владимир', 'павел', 'руслан',
    'марк', 'константин', 'тимур', 'олег', 'ярослав', 'антон', 'николай', 'глеб', 'данил',
    'савелий', 'вадим', 'степан', 'юрий', 'богдан', 'артур', 'виктор',
    # Имена латиницей
    'john', 'michael', 'william', 'james', 'david', 'robert', 'joseph', 'daniel',
    'thomas', 'matthew', 'anthony', 'donald', 'steven', 'paul', 'andrew', 'joshua',
    'kenneth', 'kevin', 'brian', 'george', 'timothy', 'ronald', 'jason', 'edward',
    'jeffrey', 'ryan', 'jacob', 'gary', 'nicholas', 'eric', 'jonathan', 'stephen',
    'larry', 'justin', 'scott', 'brandon', 'benjamin', 'samuel', 'gregory', 'alexander',
    'frank', 'patrick', 'raymond', 'jack', 'dennis', 'jerry', 'tyler', 'aaron',
    'victor', 'viktor', 
}

# Популярные женские имена
FEMALE_NAMES: Set[str] = {
    # Имена кириллицей
    'анна', 'мария', 'елена', 'дарья', 'алина', 'ирина', 'екатерина', 'арина',
    'полина', 'ольга', 'светлана', 'татьяна', 'марина', 'наталья', 'виктория', 'вика',
    'елизавета', 'анастасия', 'вероника', 'кристина', 'софия', 'юлия', 'ксения',
    'валерия', 'александра', 'василиса', 'софья', 'милана', 'дарина', 'злата',
    'надежда', 'вера', 'любовь', 'диана', 'оксана', 'евгения', 'галина', 'нина', 'маша', 'мария',
    # Имена латиницей
    'mary', 'patricia', 'jennifer', 'linda', 'elizabeth', 'barbara', 'susan', 'jessica',
    'sarah', 'karen', 'lisa', 'nancy', 'betty', 'margaret', 'sandra', 'ashley',
    'kimberly', 'emily', 'donna', 'michelle', 'carol', 'amanda', 'dorothy', 'melissa',
    'deborah', 'stephanie', 'rebecca', 'sharon', 'laura', 'cynthia', 'kathleen', 'amy',
    'angela', 'shirley', 'emma', 'anna', 'brenda', 'pamela', 'nicole', 'ruth'
}

# Имена, которые могут быть как мужскими, так и женскими
AMBIGUOUS_NAMES: Set[str] = {
    # Русские имена
    'саша', 'женя', 'валя', 'шура', 'слава', 
    # Английские имена
    'sam', 'alex', 'charlie', 'jordan', 'taylor', 'morgan', 'robin', 'ashley',
    'casey', 'jamie', 'jessie', 'kelly', 'leslie', 'pat', 'quinn', 'sydney',
    'tracy', 'val', 'winter', 'austin', 'blair', 'chris', 'drew', 'eden',
    'francis', 'harper', 'kennedy', 'lee', 'madison', 'parker', 'peyton', 'riley',
    'sage', 'skylar', 'terry', 'tyler'
}

@dataclass
class NameValidationResult:
    is_valid: bool
    gender: Gender  # 'male', 'female', 'unknown'
    reason_invalid: Optional[str] = None  # Причина невалидности, если применимо

def is_cyrillic(text: str) -> bool:
    """Проверяет, содержит ли текст кириллические символы."""
    return bool(re.search('[а-яА-Я]', text))

def contains_invalid_chars(name: str) -> bool:
    """Проверяет наличие недопустимых символов в имени."""
    # Разрешаем буквы, дефис и апостроф
    return bool(re.search(r'[^a-zA-Zа-яА-Я\-\']', name))

def is_too_short(name: str, min_length: int = 2) -> bool:
    """Проверяет, не слишком ли короткое имя."""
    return len(name.strip()) < min_length

def detect_gender_by_name(name: str) -> Gender:
    """
    Определяет пол по имени.
    
    Алгоритм:
    1. Проверяет имя в предопределенных списках популярных имен
    2. Если имя в списке неопределенных, возвращает None
    3. Для неизвестных имен пытается определить пол по окончанию (только для кириллицы)
    
    Returns:
        'male', 'female' или None, если не удалось определить
    """
    name = name.lower().strip()
    
    # Проверяем в списках популярных имен
    if name in MALE_NAMES:
        return 'male'
    if name in FEMALE_NAMES:
        return 'female'
    if name in AMBIGUOUS_NAMES:
        return "unknown"
        
    # Для неизвестных имен пытаемся определить по окончанию (только для кириллицы)
    if is_cyrillic(name):
        # Типичные окончания
        male_endings = ['й', 'н', 'р', 'т', 'в', 'м', 'к', 'с', 'л']
        female_endings = ['а', 'я', 'ь']
        
        if name.endswith(tuple(female_endings)):
            return 'female'
        elif name.endswith(tuple(male_endings)):
            return 'male'

    return "unknown"

def validate_name(name: str) -> NameValidationResult:
    """
    Комплексная валидация имени пользователя.
    
    Returns:
        NameValidationResult с результатами проверки
    """
    if not name:
        return NameValidationResult(
            is_valid=False,
            gender="unknown",
            reason_invalid="Имя отсутствует"
        )
    
    name = name.strip()
    
    if is_too_short(name):
        return NameValidationResult(
            is_valid=False,
            gender="unknown",
            reason_invalid="Имя слишком короткое"
        )
        
    if contains_invalid_chars(name):
        return NameValidationResult(
            is_valid=False,
            gender="unknown",
            reason_invalid="Имя содержит недопустимые символы"
        )
    
    gender = detect_gender_by_name(name)
    
    return NameValidationResult(
        is_valid=True,
        gender=gender,
    )

def get_name_info(name: str) -> str:
    """
    Возвращает информацию о том, как было определено имя.
    Полезно для отладки и улучшения базы имен.
    """
    name = name.lower().strip()
    if name in MALE_NAMES:
        return "Известное мужское имя"
    if name in FEMALE_NAMES:
        return "Известное женское имя"
    if name in AMBIGUOUS_NAMES:
        return "Имя может быть как мужским, так и женским"
    if is_cyrillic(name):
        return "Имя определено по окончанию (кириллица)"
    return "Имя не найдено в базе"


# Примеры использования:
if __name__ == "__main__":
    test_names = [
        # Известные имена из базы
        "Александр",   # Известное мужское имя (кириллица)
        "Elizabeth",   # Известное женское имя (латиница)
        "Саша",       # Неопределенный пол (из списка)
        "Jamie",      # Неопределенный пол (латиница)
        
        # Имена для определения по окончанию
        "Святослав",  # Мужское по окончанию
        "Любава",     # Женское по окончанию
        "Милодора",   # Женское по окончанию
        
        # Особые случаи
        "X",          # Слишком короткое
        "John123",    # Невалидные символы
        "",           # Пустое имя
        
        # Сложные случаи
        "Никита",     # Мужское, хотя окончание как у женского
        "Lee",        # Неопределяемое (латиница)
        "Женя",       # Неопределяемое (кириллица)
    ]
    
    for test_name in test_names:
        result = validate_name(test_name)
        print(f"\nИмя: {test_name}")
        print(f"Информация: {get_name_info(test_name)}")
        print(f"Результат валидации: {result}")

