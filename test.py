"""
Main test runner for Habit Tracker
Runs all tests with test database
"""
import os
import sys
from pathlib import Path

# Set TEST_MODE before importing any modules
os.environ['TEST_MODE'] = 'true'

# Import test modules
from tests.test_database import run_all_database_tests
from tests.test_validators import run_all_validator_tests
from tests.test_name_validator import run_all_name_tests

# Import database to clean up test database
from database.database import DB_PATH, initialize_database


def setup_test_database():
    """Initialize a clean test database"""
    print("=" * 60)
    print("SETTING UP TEST DATABASE")
    print("=" * 60)
    
    # Remove existing test database if it exists
    if DB_PATH.exists():
        print(f"Removing existing test database: {DB_PATH}")
        DB_PATH.unlink()
    
    # Initialize fresh database
    print(f"Initializing test database: {DB_PATH}")
    initialize_database()
    print("✅ Test database initialized\n")


def cleanup_test_database():
    """Clean up test database after tests"""
    print("\n" + "=" * 60)
    print("CLEANING UP TEST DATABASE")
    print("=" * 60)
    
    if DB_PATH.exists():
        print(f"Removing test database: {DB_PATH}")
        DB_PATH.unlink()
        print("✅ Test database removed")
    else:
        print("ℹ️ Test database not found (already removed)")


def main():
    """Main test runner"""
    print("\n" + "█" * 60)
    print("█" + " " * 58 + "█")
    print("█" + " " * 15 + "HABIT TRACKER TESTS" + " " * 24 + "█")
    print("█" + " " * 58 + "█")
    print("█" * 60 + "\n")
    
    # Setup
    setup_test_database()
    
    # Track results
    all_results = []
    
    try:
        # Run database tests
        all_results.append(("Database Tests", run_all_database_tests()))
        
        # Run validator tests (don't need database)
        all_results.append(("Validator Tests", run_all_validator_tests()))
        
        # Run name validator tests
        all_results.append(("Name Validator Tests", run_all_name_tests()))
        
    finally:
        # Always cleanup
        cleanup_test_database()
    
    # Final summary
    print("\n" + "█" * 60)
    print("█" + " " * 58 + "█")
    print("█" + " " * 18 + "FINAL SUMMARY" + " " * 27 + "█")
    print("█" + " " * 58 + "█")
    print("█" * 60)
    
    total_passed = sum(1 for _, result in all_results if result)
    total_suites = len(all_results)
    
    for suite_name, result in all_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {suite_name}: {status}")
    
    print("\n" + "─" * 60)
    print(f"  Test Suites: {total_passed}/{total_suites} passed")
    
    if total_passed == total_suites:
        print("  " + "🎉 ALL TESTS PASSED! 🎉")
        exit_code = 0
    else:
        print("  " + "⚠️  SOME TESTS FAILED")
        exit_code = 1
    
    print("█" * 60 + "\n")
    
    return exit_code


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
