# инициализируем базу данных sqlite со следующими таблицами

# users - для хранения информации о пользователях
# - telegram_id (INTEGER PRIMARY KEY) - уникальный идентификатор пользователя в Telegram
# - first_name (TEXT) - имя пользователя, как к нему обращаются
# - gender (TEXT) - пол пользователя, определяется по имени 
# - notifications_enabled (BOOLEAN) - включены ли уведомления для пользователя
# - timezone (TEXT) - часовой пояс пользователя

# habits - для хранения информации о привычках
# - telegram_id (INTEGER) - идентификатор пользователя, владеющего привычкой
# - habit_id (INTEGER PRIMARY KEY AUTOINCREMENT) - уникальный идентификатор привычки
# - name (TEXT) - название привычки
# - description (TEXT) - описание привычки
# - created_at (DATE) - дата создания привычки
# - is_active (BOOLEAN) - активна ли привычка
# - reminder_time (TIME) - время напоминания о привычке
# - schedule_days (JSON) - дни недели, в которые нужно выполнять привычку 
# (например, "{"mon": true, "tue": false, "wed": true, ...}")
# - streak_count (INTEGER) - текущая серия выполнения привычки
# - longest_streak (INTEGER) - самая длинная серия выполнения привычки

# habit_actions - для хранения информации о действиях по привычкам
# - action_id (INTEGER PRIMARY KEY AUTOINCREMENT) - уникальный идентификатор действия
# - habit_id (INTEGER) - идентификатор привычки, к которой относится действие
# - action_date (DATE) - дата выполнения действия


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
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER UNIQUE NOT NULL,
        username TEXT,
        first_name TEXT,
        last_name TEXT
    )
    """)

    # Создание таблицы привычек
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS habits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        telegram_id INTEGER NOT NULL,
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
        habit_id INTEGER NOT NULL,
        action_date DATE NOT NULL,
        is_completed BOOLEAN NOT NULL DEFAULT 0,
        FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()



