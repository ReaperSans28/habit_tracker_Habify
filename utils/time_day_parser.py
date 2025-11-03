"""
Parser for time and days from schedule string
Supports formats:
- Time: 6:30, 18:45, 6:30 am, 6:30 pm
- Days: пн, вт, пн-пт, ежедневно, daily, mon, tue, monday, etc.
Returns: JSON format {mon: true/false, tue: true/false, ...}
"""
import re
import json
from typing import Tuple, Optional, Dict, List


class TimeDayParser:
    """Parses time and day schedules for habits"""
    
    # Day mappings
    RUSSIAN_SHORT = {
        "пн": "mon", "вт": "tue", "ср": "wed", "чт": "thu",
        "пт": "fri", "сб": "sat", "вс": "sun"
    }
    
    RUSSIAN_FULL = {
        "понедельник": "mon", "вторник": "tue", "среда": "wed", "четверг": "thu",
        "пятница": "fri", "суббота": "sat", "воскресенье": "sun"
    }
    
    ENGLISH_SHORT = {
        "mon": "mon", "tue": "tue", "wed": "wed", "thu": "thu",
        "fri": "fri", "sat": "sat", "sun": "sun"
    }
    
    ENGLISH_FULL = {
        "monday": "mon", "tuesday": "tue", "wednesday": "wed", "thursday": "thu",
        "friday": "fri", "saturday": "sat", "sunday": "sun"
    }
    
    # Daily keywords
    DAILY_KEYWORDS = [
        "ежедневно", "каждый день", "все дни", "всю неделю",
        "daily", "everyday", "every day", "all days", "all"
    ]
    
    # Day order for range expansion
    DAY_ORDER = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    
    def __init__(self):
        # Combine all day mappings
        self.all_days = {**self.RUSSIAN_SHORT, **self.RUSSIAN_FULL, 
                        **self.ENGLISH_SHORT, **self.ENGLISH_FULL}
    
    def parse(self, schedule_str: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Parses schedule string into time and days.
        
        Args:
            schedule_str: String like "6:30 пн, ср, пт" or "18:00 daily"
            
        Returns:
            Tuple of (is_valid, data_dict, error_code)
            - is_valid: True if parsing successful
            - data_dict: {"time": "HH:MM", "days_json": "{\"mon\": true, ...}"}
            - error_code: Error code string or None
        """
        if not schedule_str or not schedule_str.strip():
            return False, None, "schedule_empty"
        
        schedule_str = schedule_str.strip().lower()
        
        # Extract time
        time_valid, time_str, time_error = self._parse_time(schedule_str)
        if not time_valid:
            return False, None, time_error
        
        # Remove time from string to process days
        schedule_without_time = schedule_str
        if time_str:
            # Remove the time pattern
            schedule_without_time = re.sub(
                r'\d{1,2}:\d{2}\s*(am|pm)?', 
                '', 
                schedule_str, 
                count=1
            ).strip()
        
        # Extract days
        days_valid, days_dict, days_error = self._parse_days(schedule_without_time)
        if not days_valid:
            return False, None, days_error
        
        # Convert days dict to JSON string
        days_json = json.dumps(days_dict, ensure_ascii=False)
        
        return True, {
            "time": time_str,
            "days_json": days_json
        }, None
    
    def _parse_time(self, text: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Parses time from text.
        Supports: 6:30, 18:45, 6:30 am, 6:30 pm
        """
        # Pattern for time with optional am/pm
        pattern = r'\b(\d{1,2}):(\d{2})(?:\s*(am|pm))?\b'
        match = re.search(pattern, text)
        
        if not match:
            return False, None, "time_not_found"
        
        hour_str, minute_str, meridiem = match.groups()
        hour = int(hour_str)
        minute = int(minute_str)
        
        # Handle am/pm
        if meridiem:
            if meridiem == "pm" and hour != 12:
                hour += 12
            elif meridiem == "am" and hour == 12:
                hour = 0
        
        # Validate hour and minute ranges
        if hour < 0 or hour > 23:
            return False, None, "time_invalid_hour"
        
        if minute < 0 or minute > 59:
            return False, None, "time_invalid_minute"
        
        # Format as HH:MM
        time_formatted = f"{hour:02d}:{minute:02d}"
        
        return True, time_formatted, None
    
    def _parse_days(self, text: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """
        Parses days from text.
        Supports: пн, вт, пн-пт, ежедневно, daily, mon, monday, etc.
        Returns dict: {"mon": true, "tue": false, ...}
        """
        if not text or not text.strip():
            return False, None, "days_not_found"
        
        text = text.strip().lower()
        
        # Check for daily keywords
        for keyword in self.DAILY_KEYWORDS:
            if keyword in text:
                return True, self._create_daily_dict(), None
        
        # Parse individual days and ranges
        days_set = set()
        
        # Split by commas and process each part
        parts = [p.strip() for p in text.split(",")]
        
        for part in parts:
            if not part:
                continue
            
            # Check if it's a range (пн-пт)
            if "-" in part or "–" in part:  # Support both hyphen and en-dash
                range_valid, range_days, range_error = self._parse_day_range(part)
                if not range_valid:
                    return False, None, range_error
                if range_days:
                    days_set.update(range_days)
            else:
                # Single day
                day_valid, day_code, day_error = self._parse_single_day(part)
                if not day_valid:
                    return False, None, day_error
                days_set.add(day_code)
        
        if not days_set:
            return False, None, "days_invalid"
        
        # Create dict with all days
        days_dict = {day: (day in days_set) for day in self.DAY_ORDER}
        
        return True, days_dict, None
    
    def _parse_single_day(self, day_str: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """Parses a single day string"""
        day_str = day_str.strip().lower()
        
        if day_str in self.all_days:
            return True, self.all_days[day_str], None
        
        return False, None, f"day_unknown:{day_str}"
    
    def _parse_day_range(self, range_str: str) -> Tuple[bool, Optional[List[str]], Optional[str]]:
        """
        Parses a day range like пн-пт or mon-fri
        """
        # Split by hyphen or en-dash
        separator = "-" if "-" in range_str else "–"
        parts = range_str.split(separator)
        
        if len(parts) != 2:
            return False, None, "range_invalid_format"
        
        start_str = parts[0].strip()
        end_str = parts[1].strip()
        
        # Parse start and end days
        start_valid, start_day, start_error = self._parse_single_day(start_str)
        if not start_valid:
            return False, None, start_error
        
        end_valid, end_day, end_error = self._parse_single_day(end_str)
        if not end_valid:
            return False, None, end_error
        
        # Ensure we have valid days
        if not start_day or not end_day:
            return False, None, "range_invalid_days"
        
        # Type assertions for type checker (we've validated these are not None)
        assert start_day is not None
        assert end_day is not None
        
        # Get indices
        start_idx = self.DAY_ORDER.index(start_day)
        end_idx = self.DAY_ORDER.index(end_day)
        
        # Validate that end is after start
        if end_idx <= start_idx:
            return False, None, "range_invalid_order"
        
        # Generate range
        range_days = self.DAY_ORDER[start_idx:end_idx + 1]
        
        return True, range_days, None
    
    def _create_daily_dict(self) -> Dict:
        """Creates a dict with all days set to true"""
        return {day: True for day in self.DAY_ORDER}
    
    def get_error_key(self, error_code: str) -> str:
        """Maps error codes to message keys"""
        if error_code.startswith("day_unknown:"):
            return "schedule_day_unknown"
        
        error_map = {
            "schedule_empty": "schedule_empty",
            "time_not_found": "schedule_time_not_found",
            "time_invalid_hour": "schedule_time_invalid_hour",
            "time_invalid_minute": "schedule_time_invalid_minute",
            "days_not_found": "schedule_days_not_found",
            "days_invalid": "schedule_days_invalid",
            "range_invalid_format": "schedule_range_invalid_format",
            "range_invalid_order": "schedule_range_invalid_order",
        }
        return error_map.get(error_code, "schedule_unknown_error")


# Global instance
time_day_parser = TimeDayParser()
