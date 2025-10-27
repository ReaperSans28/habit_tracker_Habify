import sqlite3
from datetime import date
from aiogram import types

DB_PATH = "habit_tracker.db"

# ---------------------------
# Инициализация базы данных
# ---------------------------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE NOT NULL,
        username TEXT,
        first_name TEXT,
        last_name TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS habits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS habit_actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        habit_id INTEGER NOT NULL,
        action_date DATE NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()

# ---------------------------
# Работа с пользователями
# ---------------------------
def add_user_if_not_exists(telegram_id: int, username: str, first_name: str, last_name: str) -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO users (telegram_id, username, first_name, last_name)
        VALUES (?, ?, ?, ?)
    """, (telegram_id, username, first_name, last_name))
    cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (telegram_id,))
    user_id = cursor.fetchone()[0]
    conn.commit()
    conn.close()
    return user_id

def get_user(telegram_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def update_username(telegram_id: int, username: str) -> str:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
            INSERT INTO users (telegram_id, username)
            VALUES (?, ?)
        """, (telegram_id, username))
    user = cursor.fetchone()
    conn.close()
    return user

def delete_user(telegram_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE telegram_id = ?", (telegram_id,))
    conn.commit()
    conn.close()

# ---------------------------
# Работа с привычками
# ---------------------------
def add_habit_for_user(telegram_user: types.User, habit_name: str, description: str = ""):
    user_id = add_user_if_not_exists(
        telegram_user.id,
        telegram_user.username or "",
        telegram_user.first_name or "",
        telegram_user.last_name or ""
    )
    add_habit(user_id, habit_name, description)

def add_habit(user_id: int, name: str, description: str = ""):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO habits (user_id, name, description) VALUES (?, ?, ?)",
                   (user_id, name, description))
    conn.commit()
    conn.close()

def get_habits(user_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM habits WHERE user_id = ?", (user_id,))
    habits = cursor.fetchall()
    conn.close()
    return habits

def delete_habit(habit_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
    conn.commit()
    conn.close()

def update_habit(habit_id: int, name: str = None, description: str = None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if name:
        cursor.execute("UPDATE habits SET name = ? WHERE id = ?", (name, habit_id))
    if description:
        cursor.execute("UPDATE habits SET description = ? WHERE id = ?", (description, habit_id))
    conn.commit()
    conn.close()

# ---------------------------
# Работа с действиями привычек
# ---------------------------
def mark_habit(habit_id: int, status: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO habit_actions (habit_id, action_date, status) VALUES (?, ?, ?)",
                   (habit_id, date.today(), status))
    conn.commit()
    conn.close()

def get_habit_actions(habit_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM habit_actions WHERE habit_id = ?", (habit_id,))
    actions = cursor.fetchall()
    conn.close()
    return actions


def get_habit_by_id(habit_id: int):
    """Возвращает привычку по её ID"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, user_id, name, description FROM habits WHERE id=?",
        (habit_id,)
    )
    habit = cursor.fetchone()
    conn.close()
    return habit
