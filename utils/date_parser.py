"""
Модуль для парсинга и валидации дат
"""
import re
from datetime import datetime, timedelta
from typing import Optional, Tuple, List
import calendar


class DateParser:
    """Класс для парсинга и работы с датами"""
    
    def __init__(self):
        # Паттерны для распознавания дат
        self.date_patterns = {
            # Форматы дат
            r'\b(\d{1,2})[./-](\d{1,2})[./-](\d{4})\b': self._parse_dd_mm_yyyy,
            r'\b(\d{4})[./-](\d{1,2})[./-](\d{1,2})\b': self._parse_yyyy_mm_dd,
            r'\b(\d{1,2})[./-](\d{1,2})\b': self._parse_dd_mm,
            
            # Относительные даты
            r'\b(сегодня|today)\b': self._parse_today,
            r'\b(завтра|tomorrow)\b': self._parse_tomorrow,
            r'\b(вчера|yesterday)\b': self._parse_yesterday,
            r'\bчерез\s+(\d+)\s+дн(?:я|ей|ь)\b': self._parse_days_from_now,
            r'\bчерез\s+(\d+)\s+нед(?:елю|ели|ель)\b': self._parse_weeks_from_now,
            r'\bчерез\s+(\d+)\s+мес(?:яц|яца|яцев)\b': self._parse_months_from_now,
            
            # Дни недели
            r'\b(понедельник|monday|пн)\b': self._parse_weekday,
            r'\b(вторник|tuesday|вт)\b': self._parse_weekday,
            r'\b(среда|wednesday|ср)\b': self._parse_weekday,
            r'\b(четверг|thursday|чт)\b': self._parse_weekday,
            r'\b(пятница|friday|пт)\b': self._parse_weekday,
            r'\b(суббота|saturday|сб)\b': self._parse_weekday,
            r'\b(воскресенье|sunday|вс)\b': self._parse_weekday,
        }
        
        # Словарь дней недели
        self.weekdays = {
            'понедельник': 0, 'monday': 0, 'пн': 0,
            'вторник': 1, 'tuesday': 1, 'вт': 1,
            'среда': 2, 'wednesday': 2, 'ср': 2,
            'четверг': 3, 'thursday': 3, 'чт': 3,
            'пятница': 4, 'friday': 4, 'пт': 4,
            'суббота': 5, 'saturday': 5, 'сб': 5,
            'воскресенье': 6, 'sunday': 6, 'вс': 6,
        }
    
    def parse_date(self, text: str) -> Optional[datetime]:
        """
        Парсит дату из текста
        Возвращает datetime объект или None если дата не найдена
        """
        text = text.lower().strip()
        
        for pattern, parser_func in self.date_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return parser_func(match)
                except (ValueError, TypeError):
                    continue
        
        return None
    
    def _parse_dd_mm_yyyy(self, match) -> datetime:
        """Парсит дату в формате DD.MM.YYYY"""
        day, month, year = map(int, match.groups())
        return datetime(year, month, day)
    
    def _parse_yyyy_mm_dd(self, match) -> datetime:
        """Парсит дату в формате YYYY.MM.DD"""
        year, month, day = map(int, match.groups())
        return datetime(year, month, day)
    
    def _parse_dd_mm(self, match) -> datetime:
        """Парсит дату в формате DD.MM (текущий год)"""
        day, month = map(int, match.groups())
        year = datetime.now().year
        return datetime(year, month, day)
    
    def _parse_today(self, match) -> datetime:
        """Парсит 'сегодня'"""
        return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    def _parse_tomorrow(self, match) -> datetime:
        """Парсит 'завтра'"""
        return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    
    def _parse_yesterday(self, match) -> datetime:
        """Парсит 'вчера'"""
        return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)
    
    def _parse_days_from_now(self, match) -> datetime:
        """Парсит 'через N дней'"""
        days = int(match.group(1))
        return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=days)
    
    def _parse_weeks_from_now(self, match) -> datetime:
        """Парсит 'через N недель'"""
        weeks = int(match.group(1))
        return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(weeks=weeks)
    
    def _parse_months_from_now(self, match) -> datetime:
        """Парсит 'через N месяцев'"""
        months = int(match.group(1))
        current = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        # Простое добавление месяцев
        year = current.year + (current.month + months - 1) // 12
        month = (current.month + months - 1) % 12 + 1
        day = min(current.day, calendar.monthrange(year, month)[1])
        return datetime(year, month, day)
    
    def _parse_weekday(self, match) -> datetime:
        """Парсит день недели"""
        weekday_name = match.group(0).lower()
        target_weekday = self.weekdays.get(weekday_name)
        
        if target_weekday is None:
            raise ValueError(f"Неизвестный день недели: {weekday_name}")
        
        current_weekday = datetime.now().weekday()
        days_ahead = target_weekday - current_weekday
        
        if days_ahead <= 0:  # Если день уже прошел на этой неделе
            days_ahead += 7
        
        return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=days_ahead)
    
    def validate_date(self, date: datetime) -> Tuple[bool, str]:
        """
        Валидирует дату
        Возвращает (is_valid, error_message)
        """
        now = datetime.now()
        
        # Проверяем, что дата не слишком далеко в прошлом
        if date < now - timedelta(days=365):
            return False, "Дата слишком далеко в прошлом (более года назад)"
        
        # Проверяем, что дата не слишком далеко в будущем
        if date > now + timedelta(days=365):
            return False, "Дата слишком далеко в будущем (более года вперед)"
        
        return True, ""
    
    def format_date(self, date: datetime) -> str:
        """Форматирует дату для отображения"""
        return date.strftime("%d.%m.%Y")
    
    def format_datetime(self, date: datetime) -> str:
        """Форматирует дату и время для отображения"""
        return date.strftime("%d.%m.%Y %H:%M")
    
    def get_relative_date(self, date: datetime) -> str:
        """Возвращает относительное описание даты"""
        now = datetime.now()
        diff = date - now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        if diff.days == 0:
            return "сегодня"
        elif diff.days == 1:
            return "завтра"
        elif diff.days == -1:
            return "вчера"
        elif diff.days > 0:
            return f"через {diff.days} дн."
        else:
            return f"{abs(diff.days)} дн. назад"


# Создаем глобальный экземпляр парсера
date_parser = DateParser()
