"""
Validator for habit input format: "название -- описание -- время и дни"
"""
from typing import Tuple, Optional


class HabitFormatValidator:
    """Validates habit input format with double-dash separator"""
    
    MIN_NAME_LENGTH = 3
    MIN_DESCRIPTION_LENGTH = 3
    SEPARATOR = "--"
    
    def __init__(self):
        pass
    
    def validate_and_split(self, user_input: str) -> Tuple[bool, Optional[dict], Optional[str]]:
        """
        Validates and splits user input into components.
        
        Args:
            user_input: Raw user input string
            
        Returns:
            Tuple of (is_valid, data_dict, error_message)
            - is_valid: True if format is correct
            - data_dict: {"name": str, "description": str, "schedule": str} or None
            - error_message: Error description or None
        """
        if not user_input or not user_input.strip():
            return False, None, "empty_input"
        
        # Split by separator
        parts = user_input.split(self.SEPARATOR)
        
        # Check if we have exactly 3 parts
        if len(parts) < 3:
            return False, None, "missing_parts"
        
        if len(parts) > 3:
            return False, None, "too_many_separators"
        
        # Extract and trim parts
        name = parts[0].strip()
        description = parts[1].strip()
        schedule = parts[2].strip()
        
        # Validate name
        if not name:
            return False, None, "empty_name"
        
        if len(name) < self.MIN_NAME_LENGTH:
            return False, None, f"name_too_short"
        
        # Validate description
        if not description:
            return False, None, "empty_description"
        
        if len(description) < self.MIN_DESCRIPTION_LENGTH:
            return False, None, f"description_too_short"
        
        # Validate schedule is not empty
        if not schedule:
            return False, None, "empty_schedule"
        
        # Success
        return True, {
            "name": name,
            "description": description,
            "schedule": schedule
        }, None
    
    def get_error_key(self, error_code: str) -> str:
        """
        Maps error codes to message keys for rendering
        """
        error_map = {
            "empty_input": "format_empty",
            "missing_parts": "format_missing_parts",
            "too_many_separators": "format_too_many_separators",
            "empty_name": "format_empty_name",
            "name_too_short": "format_name_too_short",
            "empty_description": "format_empty_description",
            "description_too_short": "format_description_too_short",
            "empty_schedule": "format_empty_schedule",
        }
        return error_map.get(error_code, "format_unknown_error")


# Global instance
habit_format_validator = HabitFormatValidator()
