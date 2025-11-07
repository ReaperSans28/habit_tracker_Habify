"""
Test validation utilities
Tests habit format validator and time/day parser
"""
import sys
from pathlib import Path

# Ensure we can import from parent directory
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.habit_format_validator import habit_format_validator
from utils.time_day_parser import time_day_parser
import json


def test_habit_format_validator():
    """Test habit format validation"""
    print("\nTesting habit format validator...")
    
    try:
        # Test valid input
        valid_input = "Бег -- Утренняя пробежка 5км -- 6:30 ежедневно"
        is_valid, data, error = habit_format_validator.validate_and_split(valid_input)
        assert is_valid == True, "Valid input should pass"
        assert data["name"] == "Бег"
        assert data["description"] == "Утренняя пробежка 5км"
        assert data["schedule"] == "6:30 ежедневно"
        print("✅ Valid format accepted")
        
        # Test empty input
        is_valid, data, error = habit_format_validator.validate_and_split("")
        assert is_valid == False
        assert error == "empty_input"
        print("✅ Empty input rejected")
        
        # Test missing parts
        is_valid, data, error = habit_format_validator.validate_and_split("Только название")
        assert is_valid == False
        assert error == "missing_parts"
        print("✅ Missing parts rejected")
        
        # Test too many separators
        is_valid, data, error = habit_format_validator.validate_and_split("A -- B -- C -- D")
        assert is_valid == False
        assert error == "too_many_separators"
        print("✅ Too many separators rejected")
        
        # Test short name
        is_valid, data, error = habit_format_validator.validate_and_split("AB -- Description -- 8:00 daily")
        assert is_valid == False
        assert "name_too_short" in error
        print("✅ Short name rejected")
        
        # Test short description
        is_valid, data, error = habit_format_validator.validate_and_split("Name -- AB -- 8:00 daily")
        assert is_valid == False
        assert "description_too_short" in error
        print("✅ Short description rejected")
        
        return True
        
    except Exception as e:
        print(f"❌ Habit format validator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_time_day_parser():
    """Test time and day parsing"""
    print("\nTesting time and day parser...")
    
    try:
        # Test daily schedule
        is_valid, data, error = time_day_parser.parse("6:30 ежедневно")
        assert is_valid == True, "Valid daily schedule should pass"
        assert data["time"] == "06:30"
        days_dict = json.loads(data["days_json"])
        assert all(days_dict.values()), "All days should be true for 'ежедневно'"
        print("✅ Daily schedule parsed correctly")
        
        # Test specific days (Russian)
        is_valid, data, error = time_day_parser.parse("18:00 пн, ср, пт")
        assert is_valid == True
        assert data["time"] == "18:00"
        days_dict = json.loads(data["days_json"])
        assert days_dict["mon"] == True
        assert days_dict["wed"] == True
        assert days_dict["fri"] == True
        assert days_dict["tue"] == False
        print("✅ Specific days (Russian) parsed correctly")
        
        # Test day range
        is_valid, data, error = time_day_parser.parse("9:00 пн-пт")
        assert is_valid == True
        assert data["time"] == "09:00"
        days_dict = json.loads(data["days_json"])
        assert days_dict["mon"] == True
        assert days_dict["tue"] == True
        assert days_dict["wed"] == True
        assert days_dict["thu"] == True
        assert days_dict["fri"] == True
        assert days_dict["sat"] == False
        assert days_dict["sun"] == False
        print("✅ Day range parsed correctly")
        
        # Test AM/PM format
        is_valid, data, error = time_day_parser.parse("6:30 pm daily")
        assert is_valid == True
        assert data["time"] == "18:30"
        print("✅ AM/PM format parsed correctly")
        
        # Test English days
        is_valid, data, error = time_day_parser.parse("10:00 mon, wed, fri")
        assert is_valid == True
        days_dict = json.loads(data["days_json"])
        assert days_dict["mon"] == True
        assert days_dict["wed"] == True
        assert days_dict["fri"] == True
        print("✅ English days parsed correctly")
        
        # Test invalid time
        is_valid, data, error = time_day_parser.parse("25:00 daily")
        assert is_valid == False
        assert "time_invalid_hour" in error
        print("✅ Invalid hour rejected")
        
        # Test missing time
        is_valid, data, error = time_day_parser.parse("daily")
        assert is_valid == False
        assert "time_not_found" in error
        print("✅ Missing time rejected")
        
        # Test invalid day
        is_valid, data, error = time_day_parser.parse("8:00 invalid_day")
        assert is_valid == False
        print("✅ Invalid day rejected")
        
        return True
        
    except Exception as e:
        print(f"❌ Time/day parser test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_validator_tests():
    """Run all validator tests"""
    print("=" * 60)
    print("RUNNING VALIDATOR TESTS")
    print("=" * 60)
    
    results = []
    
    results.append(("Habit Format Validator", test_habit_format_validator()))
    results.append(("Time and Day Parser", test_time_day_parser()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("=" * 60)
    
    return passed == total


if __name__ == "__main__":
    run_all_validator_tests()
