# инициализируем базу данных sqlite со следующими таблицами

# users - для хранения информации о пользователях
# - telegram_id (INTEGER PRIMARY KEY) - уникальный идентификатор пользователя в Telegram
# - first_name (TEXT) - имя пользователя, как к нему обращаются
# - gender (TEXT) - пол пользователя, определяется по имени 
# - notifications_enabled (BOOLEAN) - включены ли уведомления для пользователя


# habits - для хранения информации о привычках
# - telegram_id (INTEGER) - идентификатор пользователя, владеющего привычкой
# - habit_id (INTEGER PRIMARY KEY AUTOINCREMENT) - уникальный идентификатор привычки
# - name (TEXT) - название привычки
# - description (TEXT) - описание привычки
# - created_at (DATE) - дата создания привычки
# - is_active (BOOLEAN) - активна ли привычка
# - reminder_time (TIME) - время напоминания о привычке
# - schedule_days (JSON) - дни недели, в которые нужно выполнять привычку 
# - streak_count (INTEGER) - текущая серия выполнения привычки
# - longest_streak (INTEGER) - самая длинная серия выполнения привычки

# habit_actions - для хранения информации о действиях по привычкам
# - action_id (INTEGER PRIMARY KEY AUTOINCREMENT) - уникальный идентификатор действия
# - habit_id (INTEGER) - идентификатор привычки, к которой относится действие
# - action_date (DATE) - дата выполнения действия
# - is_completed (BOOLEAN) - хранит результат  


DB_FOLDER = "data"
DB_FILE = "database.sqlite"

from typing import Optional
from pathlib import Path
import sqlite3
import pandas as pd

DB_PATH = Path(DB_FOLDER) / DB_FILE

def create_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

def initialize_database():
    Path(DB_FOLDER).mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Создание таблицы пользователей
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        telegram_id INTEGER UNIQUE NOT NULL,
        first_name TEXT,
        gender TEXT,
        notifications_enabled BOOLEAN
        
    )
    """)

    # Создание таблицы привычек
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS habits (
        habit_id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER,
        name TEXT NOT NULL,
        description TEXT,
        created_at DATE NOT NULL,
        is_active BOOLEAN NOT NULL DEFAULT 1,
        reminder_time TIME,
        schedule_days TEXT,
        streak_count INTEGER DEFAULT 0,
        longest_streak INTEGER DEFAULT 0,
        FOREIGN KEY (telegram_id) REFERENCES users(telegram_id) ON DELETE CASCADE
    )
    """)

    # Создание таблицы действий по привычкам
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS habit_actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        habit_id INTEGER,
        action_date DATE NOT NULL,
        is_completed BOOLEAN NOT NULL DEFAULT 0,
        FOREIGN KEY (habit_id) REFERENCES habits(habit_id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()

# Функции для взаимодействия с базой данных

def get_user(telegram_id: int) -> Optional[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row is not None else None



def add_user(telegram_id: int, 
             first_name: str, 
             gender: str, 
             notifications_enabled: bool):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""INSERT OR IGNORE INTO users (telegram_id, first_name, gender, notifications_enabled) 
                   VALUES (?, ?, ?, ?)""",
                   (telegram_id, first_name, gender, notifications_enabled)
                   )
    conn.commit()
    conn.close()

def add_habit(
        telegram_id: int, 
        name: str, 
        description: str, 
        created_at: str, 
        is_active: str, 
        reminder_time: str, 
        schedule_days: str, 
        streak_count: str, 
        longest_streak: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
                   INSERT OR IGNORE INTO habits 
                        (telegram_id, name, description, created_at, 
                        is_active, reminder_time, schedule_days, streak_count, longest_streak) 
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                   (telegram_id, name, description, created_at, 
                    is_active, reminder_time, schedule_days, streak_count, longest_streak))
    conn.commit()
    conn.close()

def get_active_habits(telegram_id: int) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM habits WHERE telegram_id = ? AND is_active = 1"
    df = pd.read_sql_query(query, conn, params=(telegram_id,))
    conn.close()
    return df

def list_habits(telegram_id: int) -> list:
    """
    Returns list of all habits for a user (for habit list display).
    Returns: List of tuples (habit_id, name, is_active, reminder_time)
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT habit_id, name, is_active, reminder_time 
        FROM habits 
        WHERE telegram_id = ? 
        ORDER BY created_at DESC
    """, (telegram_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_habit(habit_id: int) -> Optional[dict]:
    """
    Returns single habit by ID as dictionary.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM habits WHERE habit_id = ?", (habit_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row is not None else None

def edit_habit(habit_id: int, name: str, description: str, reminder_time: str, schedule_days: str):
    """
    Updates all editable fields of a habit.
    Used when user edits habit via "Редактировать" flow.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE habits 
        SET name = ?, description = ?, reminder_time = ?, schedule_days = ?
        WHERE habit_id = ?
    """, (name, description, reminder_time, schedule_days, habit_id))
    conn.commit()
    conn.close()

def change_active(habit_id: int, is_active: bool):
    """
    Toggle habit active/paused state.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE habits SET is_active = ? WHERE habit_id = ?", (is_active, habit_id))
    conn.commit()
    conn.close()
    
def delete_habit(habit_id: int):
    """
    Deletes a habit. Related habit_actions will be cascade deleted.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM habits WHERE habit_id = ?", (habit_id,))
    conn.commit()
    conn.close()

def add_habit_action(habit_id: int, action_date: str, is_completed: bool):
    """
    Records a habit action (completion/skip for a date).
    Used when user marks habit as done or skipped.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO habit_actions (habit_id, action_date, is_completed) 
        VALUES (?, ?, ?)
    """, (habit_id, action_date, is_completed))
    conn.commit()
    conn.close()


# ============================================================================
# NAMESPACE STRUCTURE: db.table.method()
# ============================================================================

class UsersTable:
    """Operations on users table"""
    
    @staticmethod
    def get_user(telegram_id: int) -> Optional[dict]:
        return get_user(telegram_id)
    
    @staticmethod
    def add_user(telegram_id: int, first_name: str, gender: str, notifications_enabled: bool):
        return add_user(telegram_id, first_name, gender, notifications_enabled)


class HabitsTable:
    """Operations on habits table"""
    
    @staticmethod
    def add_habit(telegram_id: int, name: str, description: str, created_at: str, 
                  is_active: str, reminder_time: str, schedule_days: str, 
                  streak_count: str, longest_streak: str):
        return add_habit(telegram_id, name, description, created_at, is_active, 
                        reminder_time, schedule_days, streak_count, longest_streak)
    
    @staticmethod
    def list_habits(telegram_id: int) -> list:
        """Returns list of tuples (habit_id, name, is_active, reminder_time)"""
        return list_habits(telegram_id)
    
    @staticmethod
    def get_habit(habit_id: int) -> Optional[dict]:
        return get_habit(habit_id)
    
    @staticmethod
    def edit_habit(habit_id: int, name: str, description: str, 
                   reminder_time: str, schedule_days: str):
        return edit_habit(habit_id, name, description, reminder_time, schedule_days)
    
    @staticmethod
    def change_active(habit_id: int, is_active: bool):
        return change_active(habit_id, is_active)
    
    @staticmethod
    def delete(habit_id: int):
        return delete_habit(habit_id)
    
    @staticmethod
    def get_active_habits(telegram_id: int) -> pd.DataFrame:
        """Legacy function for compatibility - returns DataFrame"""
        return get_active_habits(telegram_id)


class HabitActionsTable:
    """Operations on habit_actions table"""
    
    @staticmethod
    def add_action(habit_id: int, action_date: str, is_completed: bool):
        """Record habit completion"""
        return add_habit_action(habit_id, action_date, is_completed)


class DB:
    """Database namespace - use db.users.method(), db.habits.method(), db.habit_actions.method()"""
    users = UsersTable
    habits = HabitsTable
    habit_actions = HabitActionsTable


# Export the namespace instance
db = DB()
