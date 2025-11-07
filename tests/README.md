# Test Suite for Habit Tracker

This folder contains automated tests for the Habit Tracker bot.

## Test Files

### `test_database.py`
Tests all database operations:
- ✅ Database initialization
- ✅ User CRUD operations (create, read)
- ✅ Habit CRUD operations (create, read, update, delete)
- ✅ Habit activation/deactivation
- ✅ Habit actions (marking as done)
- ✅ Cascade deletion

### `test_validators.py`
Tests input validation utilities:
- ✅ Habit format validation ("название -- описание -- время и дни")
- ✅ Time parsing (6:30, 18:45, 6:30 am, 9:00 pm)
- ✅ Day parsing (ежедневно, пн-пт, пн, ср, пт, daily, mon-fri, etc.)
- ✅ Error handling for invalid inputs

### `test_name_validator.py`
Tests name validation and gender detection:
- ✅ Valid name acceptance
- ✅ Gender detection (male/female/unknown)
- ✅ Invalid character rejection
- ✅ Length validation

## Running Tests

### Run all tests:
```bash
python test.py
```

### Run individual test suites:
```bash
# Database tests only
python tests/test_database.py

# Validator tests only
python tests/test_validators.py

# Name validator tests only
python tests/test_name_validator.py
```

## Test Database

Tests use a separate test database (`database_test.sqlite`) which is:
- Created automatically before tests run
- Cleaned up automatically after tests complete
- Isolated from the production database

The test mode is controlled by the `TEST_MODE` environment variable in `.env` file.

## Test Output

Tests provide detailed output:
- ✅ Green checkmarks for passing tests
- ❌ Red X marks for failing tests
- Detailed error messages and stack traces for debugging
- Summary statistics at the end

## Adding New Tests

To add new tests:

1. Create a new test file in `tests/` folder
2. Import it in `test.py`
3. Add it to the test runner in `main()` function
4. Follow the naming convention: `test_*.py`

Example test structure:
```python
def test_something():
    """Test description"""
    print("\\nTesting something...")
    try:
        # Test code
        assert condition, "Error message"
        print("✅ Test passed")
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def run_all_tests():
    results = []
    results.append(("Test Name", test_something()))
    # Print summary
    return all(results)
```
