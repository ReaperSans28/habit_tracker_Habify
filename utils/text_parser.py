"""
Модуль для парсинга текстовых данных
"""
import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from .date_parser import date_parser


class TextParser:
    """Класс для парсинга текстовых данных"""
    
    def __init__(self):
        # Паттерны для извлечения информации
        self.patterns = {
            'frequency': [
                r'каждый\s+день',
                r'ежедневно',
                r'раз\s+в\s+день',
                r'каждый\s+(\d+)\s+дн(?:я|ей|ь)',
                r'раз\s+в\s+(\d+)\s+дн(?:я|ей|ь)',
                r'каждые\s+(\d+)\s+дн(?:я|ей|ь)',
                r'каждую\s+неделю',
                r'раз\s+в\s+неделю',
                r'каждые\s+(\d+)\s+нед(?:елю|ели|ель)',
                r'раз\s+в\s+(\d+)\s+нед(?:елю|ели|ель)',
                r'каждый\s+месяц',
                r'раз\s+в\s+месяц',
                r'каждые\s+(\d+)\s+мес(?:яц|яца|яцев)',
                r'раз\s+в\s+(\d+)\s+мес(?:яц|яца|яцев)',
            ],
            'time': [
                r'в\s+(\d{1,2}):(\d{2})',
                r'в\s+(\d{1,2})\s+час(?:а|ов)?',
                r'в\s+(\d{1,2})\s+утра',
                r'в\s+(\d{1,2})\s+вечера',
                r'утром',
                r'днем',
                r'вечером',
                r'ночью',
            ],
            'duration': [
                r'(\d+)\s+мин(?:ут|уты|уты)?',
                r'(\d+)\s+час(?:а|ов)?',
                r'(\d+)\s+ч\.',
                r'(\d+)\s+м\.',
            ],
            'reminder': [
                r'напомни\s+мне',
                r'напомнить',
                r'уведомить',
                r'уведомление',
            ]
        }
    
    def parse_habit_text(self, text: str) -> Dict:
        """
        Парсит текст привычки и извлекает структурированную информацию
        """
        result = {
            'name': text.strip(),
            'frequency': None,
            'time': None,
            'duration': None,
            'reminder': False,
            'dates': [],
            'parsed_successfully': True,
            'errors': []
        }
        
        # Извлекаем даты
        dates = self._extract_dates(text)
        result['dates'] = dates
        
        # Извлекаем частоту
        frequency = self._extract_frequency(text)
        result['frequency'] = frequency
        
        # Извлекаем время
        time_info = self._extract_time(text)
        result['time'] = time_info
        
        # Извлекаем продолжительность
        duration = self._extract_duration(text)
        result['duration'] = duration
        
        # Проверяем наличие напоминаний
        result['reminder'] = self._has_reminder(text)
        
        # Очищаем название от служебной информации
        result['name'] = self._clean_habit_name(text, result)
        
        return result
    
    def _extract_dates(self, text: str) -> List[datetime]:
        """Извлекает даты из текста"""
        dates = []
        words = text.split()
        
        # Проверяем каждое слово и комбинации слов
        for i in range(len(words)):
            for j in range(i + 1, min(i + 5, len(words) + 1)):
                phrase = ' '.join(words[i:j])
                date = date_parser.parse_date(phrase)
                if date:
                    is_valid, error = date_parser.validate_date(date)
                    if is_valid:
                        dates.append(date)
                    else:
                        # Пропускаем невалидные даты
                        pass
        
        return dates
    
    def _extract_frequency(self, text: str) -> Optional[Dict]:
        """Извлекает информацию о частоте"""
        text_lower = text.lower()
        
        for pattern in self.patterns['frequency']:
            match = re.search(pattern, text_lower)
            if match:
                if 'каждый день' in pattern or 'ежедневно' in pattern or 'раз в день' in pattern:
                    return {'type': 'daily', 'interval': 1}
                elif 'каждую неделю' in pattern or 'раз в неделю' in pattern:
                    return {'type': 'weekly', 'interval': 1}
                elif 'каждый месяц' in pattern or 'раз в месяц' in pattern:
                    return {'type': 'monthly', 'interval': 1}
                elif match.groups():
                    # Есть числовое значение
                    number = int(match.group(1))
                    if 'дн' in pattern:
                        return {'type': 'daily', 'interval': number}
                    elif 'нед' in pattern:
                        return {'type': 'weekly', 'interval': number}
                    elif 'мес' in pattern:
                        return {'type': 'monthly', 'interval': number}
        
        return None
    
    def _extract_time(self, text: str) -> Optional[Dict]:
        """Извлекает информацию о времени"""
        text_lower = text.lower()
        
        for pattern in self.patterns['time']:
            match = re.search(pattern, text_lower)
            if match:
                if ':' in pattern:
                    hour, minute = map(int, match.groups())
                    return {'hour': hour, 'minute': minute, 'type': 'exact'}
                elif 'час' in pattern:
                    hour = int(match.group(1))
                    return {'hour': hour, 'minute': 0, 'type': 'exact'}
                elif 'утра' in pattern:
                    hour = int(match.group(1))
                    return {'hour': hour, 'minute': 0, 'type': 'morning'}
                elif 'вечера' in pattern:
                    hour = int(match.group(1)) + 12
                    return {'hour': hour, 'minute': 0, 'type': 'evening'}
                elif 'утром' in pattern:
                    return {'hour': 9, 'minute': 0, 'type': 'morning'}
                elif 'днем' in pattern:
                    return {'hour': 14, 'minute': 0, 'type': 'afternoon'}
                elif 'вечером' in pattern:
                    return {'hour': 19, 'minute': 0, 'type': 'evening'}
                elif 'ночью' in pattern:
                    return {'hour': 23, 'minute': 0, 'type': 'night'}
        
        return None
    
    def _extract_duration(self, text: str) -> Optional[Dict]:
        """Извлекает информацию о продолжительности"""
        text_lower = text.lower()
        
        for pattern in self.patterns['duration']:
            match = re.search(pattern, text_lower)
            if match:
                value = int(match.group(1))
                if 'мин' in pattern:
                    return {'value': value, 'unit': 'minutes'}
                elif 'час' in pattern or 'ч.' in pattern:
                    return {'value': value, 'unit': 'hours'}
        
        return None
    
    def _has_reminder(self, text: str) -> bool:
        """Проверяет, есть ли в тексте запрос на напоминание"""
        text_lower = text.lower()
        
        for pattern in self.patterns['reminder']:
            if re.search(pattern, text_lower):
                return True
        
        return False
    
    def _clean_habit_name(self, text: str, parsed_data: Dict) -> str:
        """Очищает название привычки от служебной информации"""
        cleaned = text
        
        # Удаляем временные маркеры
        for pattern in self.patterns['time']:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Удаляем маркеры продолжительности
        for pattern in self.patterns['duration']:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Удаляем маркеры напоминаний
        for pattern in self.patterns['reminder']:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE)
        
        # Удаляем лишние пробелы
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        
        return cleaned if cleaned else text


# Создаем глобальный экземпляр парсера
text_parser = TextParser()
