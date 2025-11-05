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
        is_active BOOLEAN,
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

###########################################################################
import pd

def get_active_habits(telegram_id: int) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT * FROM habits WHERE telegram_id = ? AND is_active = 1"
    df = pd.read_sql_query(query, conn, params=(telegram_id,))
    conn.close()
    return df

def get_habbit(telegram_id: int, name: str, description: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM habits WHERE telegram_id = ? AND name = ? AND description = ?", (telegram_id, name, description))
    result = cursor.fetchall()
    conn.close()
    return result
    
       
def add_habit_actions(action_date: str, is_completed: bool):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""INSERT OR IGNORE INTO habit_actions (action_date, is_completed) VALUES (?, ?)""",
                   (action_date, is_completed))
    conn.commit()
    conn.close()
    
def add_is_active(telegram_id: int, is_active: bool):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE habits SET is_active = ? WHERE telegram_id = ?", (telegram_id, is_active))
    conn.commit()
    conn.close()
    
def add_is_completed(telegram_id: int, is_completed: bool):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE habit_actions SET is_completed = ? WHERE telegram_id = ?", (telegram_id, is_completed))
    conn.commit()
    conn.close()


def edit_habit(telegram_id: int, description: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE habits SET description = ? WHERE telegram_id = ?", (telegram_id, description))
    conn.commit()
    conn.close()
    
def delete_habit(habit_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM habits WHERE habit_id = ?", (habit_id,))
    conn.commit()
    conn.close()
    
def delete_habit_action(id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM habit_actions WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    
def edit_notifications_enabled(telegram_id: int, notifications_enabled: bool):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET notifications_enabled = ? WHERE telegram_id = ?", (telegram_id, notifications_enabled))
    conn.commit()
    conn.close()
    
    
# В разработке
def add_streak(telegram_id: int, streak_count: int, is_completed: bool, is_active: bool):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM habits WHERE telegram_id = ? AND is_completed = ?", (telegram_id, is_completed))
    
    if is_active and is_completed:
        cursor.execute("""UPDATE habits SET streak_count = streak_count + 1 WHERE telegram_id + ?""")

    
def get_streak(telegram_id: int, streak_count: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM habits WHERE telegram_id = ? AND streak_count = ?", (telegram_id, streak_count))
    result = cursor.fetchall()
    conn.close()
    return result
    

    