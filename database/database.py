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
        action_date DATE NOT NULL,
        is_completed BOOLEAN NOT NULL DEFAULT 0,
        FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()

# 
def add_habit_actions(action_date: str, is_completed: bool):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""INSERT OR IGNORE INTO users (action_date, is_completed) VALUES (?, ?)""",
                   (action_date, is_completed))
    conn.commit()
    conn.close()
    
def get_user(telegram_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE telegram_id = ?", (telegram_id,))
    user = cursor.fetchone()
    conn.close()
    return user

def add_habit(telegram_id: int, name: str, description: str, created_at: str, is_active: str, reminder_time: str, schedule_days: str, streak_count: str, longest_streak: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""INSERT OR IGNORE INTO users (telegram_id, name, description, created_at, is_active, reminder_time, schedule_days, streak_count, longest_streak) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                   (telegram_id, name, description, created_at, is_active, reminder_time, schedule_days, streak_count, longest_streak))
    conn.commit()
    conn.close()
       
    
def add_user(telegram_id: int, first_name: str, gender: str, notifications_enabled: bool):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""INSERT OR IGNORE INTO users (telegram_id, first_name, gender, notifications_enabled) VALUES (?, ?, ?, ?)""",
                   (telegram_id, first_name, gender, notifications_enabled))
    conn.commit()
    conn.close()