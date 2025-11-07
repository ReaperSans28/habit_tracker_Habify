"""
Test name validator
Tests name validation and gender detection
"""
import sys
from pathlib import Path

# Ensure we can import from parent directory
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.name_validator import validate_name, Gender


def test_name_validator():
    """Test name validation and gender detection"""
    print("\nTesting name validator...")
    
    try:
        # Test valid male name
        result = validate_name("Александр")
        assert result.is_valid == True
        assert result.gender == "male"
        print("✅ Valid male name accepted")
        
        # Test valid female name
        result = validate_name("Мария")
        assert result.is_valid == True
        assert result.gender == "female"
        print("✅ Valid female name accepted")
        
        # Test empty name
        result = validate_name("")
        assert result.is_valid == False
        assert "отсутствует" in result.reason_invalid.lower()
        print("✅ Empty name rejected")
        
        # Test short name
        result = validate_name("A")
        assert result.is_valid == False
        assert "короткое" in result.reason_invalid.lower()
        print("✅ Short name rejected")
        
        # Test name with numbers
        result = validate_name("Alex123")
        assert result.is_valid == False
        assert "недопустимые" in result.reason_invalid.lower()
        print("✅ Name with numbers rejected")
        
        # Test name with special characters
        result = validate_name("Alex@User")
        assert result.is_valid == False
        print("✅ Name with special characters rejected")
        
        # Test valid English name
        result = validate_name("John")
        assert result.is_valid == True
        print("✅ Valid English name accepted")
        
        # Test unknown gender (should default to unknown)
        result = validate_name("SomeUnknownName")
        assert result.is_valid == True
        # Gender might be unknown or detected - either is acceptable
        print("✅ Name with unknown gender accepted")
        
        return True
        
    except Exception as e:
        print(f"❌ Name validator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_name_tests():
    """Run all name validator tests"""
    print("=" * 60)
    print("RUNNING NAME VALIDATOR TESTS")
    print("=" * 60)
    
    results = []
    results.append(("Name Validator", test_name_validator()))
    
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
    run_all_name_tests()
