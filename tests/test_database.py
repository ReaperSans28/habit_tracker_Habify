"""
Test database operations
Tests CRUD operations for users, habits, and habit_actions
"""
import sys
from pathlib import Path

# Ensure we can import from parent directory
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.database import db, initialize_database
import json


def test_database_initialization():
    """Test that database initializes correctly"""
    print("Testing database initialization...")
    try:
        initialize_database()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False


def test_user_operations():
    """Test user CRUD operations"""
    print("\nTesting user operations...")
    
    test_user_id = 123456789
    test_name = "TestUser"
    test_gender = "male"
    
    try:
        # Test add_user
        db.users.add_user(test_user_id, test_name, test_gender, True)
        print("✅ User added successfully")
        
        # Test get_user
        user = db.users.get_user(test_user_id)
        assert user is not None, "User should exist"
        assert user["telegram_id"] == test_user_id
        assert user["first_name"] == test_name
        assert user["gender"] == test_gender
        print("✅ User retrieved successfully")
        
        # Test duplicate add (should be ignored)
        db.users.add_user(test_user_id, "DifferentName", "female", False)
        user = db.users.get_user(test_user_id)
        assert user["first_name"] == test_name, "Duplicate insert should be ignored"
        print("✅ Duplicate user insertion ignored correctly")
        
        return True
    except Exception as e:
        print(f"❌ User operations failed: {e}")
        return False


def test_habit_operations():
    """Test habit CRUD operations"""
    print("\nTesting habit operations...")
    
    test_user_id = 123456789
    
    try:
        # Test add_habit
        from datetime import datetime
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        schedule_days = json.dumps({
            "mon": True, "tue": True, "wed": True, "thu": True,
            "fri": True, "sat": False, "sun": False
        })
        
        db.habits.add_habit(
            telegram_id=test_user_id,
            name="Тестовая привычка",
            description="Описание тестовой привычки",
            created_at=created_at,
            is_active="1",
            reminder_time="08:00",
            schedule_days=schedule_days,
            streak_count="0",
            longest_streak="0"
        )
        print("✅ Habit added successfully")
        
        # Test list_habits
        habits = db.habits.list_habits(test_user_id)
        assert len(habits) > 0, "Should have at least one habit"
        habit_id = habits[0][0]  # (habit_id, name, is_active, reminder_time)
        print(f"✅ Habit listed successfully (ID: {habit_id})")
        
        # Test get_habit
        habit = db.habits.get_habit(habit_id)
        assert habit is not None, "Habit should exist"
        assert habit["name"] == "Тестовая привычка"
        assert habit["reminder_time"] == "08:00"
        print("✅ Habit retrieved successfully")
        
        # Test edit_habit
        new_schedule = json.dumps({
            "mon": True, "tue": False, "wed": True, "thu": False,
            "fri": True, "sat": False, "sun": False
        })
        
        db.habits.edit_habit(
            habit_id=habit_id,
            name="Обновленная привычка",
            description="Новое описание",
            reminder_time="09:30",
            schedule_days=new_schedule
        )
        
        habit = db.habits.get_habit(habit_id)
        assert habit["name"] == "Обновленная привычка"
        assert habit["reminder_time"] == "09:30"
        print("✅ Habit edited successfully")
        
        # Test change_active
        db.habits.change_active(habit_id, False)
        habit = db.habits.get_habit(habit_id)
        is_active = bool(int(habit["is_active"])) if isinstance(habit["is_active"], str) else bool(habit["is_active"])
        assert is_active == False, "Habit should be inactive"
        print("✅ Habit deactivated successfully")
        
        db.habits.change_active(habit_id, True)
        habit = db.habits.get_habit(habit_id)
        is_active = bool(int(habit["is_active"])) if isinstance(habit["is_active"], str) else bool(habit["is_active"])
        assert is_active == True, "Habit should be active"
        print("✅ Habit activated successfully")
        
        # Test get_active_habits (legacy function)
        active_df = db.habits.get_active_habits(test_user_id)
        assert not active_df.empty, "Should have active habits"
        print("✅ Active habits retrieved successfully")
        
        return habit_id  # Return for use in habit_actions tests
        
    except Exception as e:
        print(f"❌ Habit operations failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_habit_actions(habit_id):
    """Test habit_actions operations"""
    print("\nTesting habit actions...")
    
    if not habit_id:
        print("⚠️ Skipping habit actions test (no habit_id)")
        return False
    
    try:
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        
        # Test add_action
        db.habit_actions.add_action(habit_id, today, True)
        print("✅ Habit action added successfully")
        
        # Note: We don't have a get_actions function, so we can't verify
        # but if no exception was raised, it worked
        
        return True
        
    except Exception as e:
        print(f"❌ Habit actions operations failed: {e}")
        return False


def test_habit_deletion(habit_id):
    """Test habit deletion (should cascade to habit_actions)"""
    print("\nTesting habit deletion...")
    
    if not habit_id:
        print("⚠️ Skipping deletion test (no habit_id)")
        return False
    
    try:
        # Delete habit
        db.habits.delete(habit_id)
        print("✅ Habit deleted successfully")
        
        # Verify it's gone
        habit = db.habits.get_habit(habit_id)
        assert habit is None, "Habit should not exist after deletion"
        print("✅ Habit deletion verified")
        
        return True
        
    except Exception as e:
        print(f"❌ Habit deletion failed: {e}")
        return False


def run_all_database_tests():
    """Run all database tests"""
    print("=" * 60)
    print("RUNNING DATABASE TESTS")
    print("=" * 60)
    
    results = []
    
    # Initialize database
    results.append(("Database Initialization", test_database_initialization()))
    
    # User operations
    results.append(("User Operations", test_user_operations()))
    
    # Habit operations
    habit_id = test_habit_operations()
    results.append(("Habit Operations", habit_id is not None))
    
    # Habit actions
    results.append(("Habit Actions", test_habit_actions(habit_id)))
    
    # Deletion
    results.append(("Habit Deletion", test_habit_deletion(habit_id)))
    
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
    run_all_database_tests()
