"""
База данных - функции для работы с SQLite
Асинхронная работа через aiosqlite
"""

import aiosqlite
from datetime import datetime
from config import DATABASE_PATH

# Глобальное подключение
db_connection = None


async def init_db():
    """Инициализация базы данных и создание таблиц"""
    global db_connection
    
    db_connection = await aiosqlite.connect(DATABASE_PATH)
    db_connection.row_factory = aiosqlite.Row
    
    # Создание таблиц
    await db_connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            username TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    await db_connection.execute("""
        CREATE TABLE IF NOT EXISTS documents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            doc_type TEXT NOT NULL,
            number TEXT NOT NULL,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            payer TEXT NOT NULL,
            file_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    """)
    
    # Создание индексов для ускорения поиска
    await db_connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_documents_user_id 
        ON documents (user_id)
    """)
    
    await db_connection.execute("""
        CREATE INDEX IF NOT EXISTS idx_documents_type 
        ON documents (doc_type)
    """)
    
    await db_connection.commit()
    
    print("Таблицы базы данных созданы/проверены")


async def get_db():
    """Получение подключения к базе данных"""
    return db_connection


async def add_user(user_id: int, username: str = None):
    """Добавление пользователя в базу"""
    try:
        await db_connection.execute(
            "INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)",
            (user_id, username)
        )
        await db_connection.commit()
    except Exception as e:
        print(f"Ошибка добавления пользователя: {e}")


async def add_document(
    user_id: int,
    doc_type: str,
    number: str,
    date: str,
    description: str,
    amount: float,
    payer: str,
    file_path: str = None
):
    """Добавление документа в базу"""
    try:
        cursor = await db_connection.execute(
            """
            INSERT INTO documents 
            (user_id, doc_type, number, date, description, amount, payer, file_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, doc_type, number, date, description, amount, payer, file_path)
        )
        await db_connection.commit()
        return cursor.lastrowid
    except Exception as e:
        print(f"Ошибка добавления документа: {e}")
        return None


async def get_user_documents(user_id: int):
    """Получение всех документов пользователя"""
    try:
        cursor = await db_connection.execute(
            """
            SELECT * FROM documents 
            WHERE user_id = ? 
            ORDER BY created_at DESC
            """,
            (user_id,)
        )
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
    except Exception as e:
        print(f"Ошибка получения документов: {e}")
        return []


async def get_document_by_id(doc_id: int, user_id: int):
    """Получение документа по ID"""
    try:
        cursor = await db_connection.execute(
            """
            SELECT * FROM documents 
            WHERE id = ? AND user_id = ?
            """,
            (doc_id, user_id)
        )
        row = await cursor.fetchone()
        return dict(row) if row else None
    except Exception as e:
        print(f"Ошибка получения документа: {e}")
        return None


async def update_document_file(doc_id: int, file_path: str):
    """Обновление пути к файлу документа"""
    try:
        await db_connection.execute(
            "UPDATE documents SET file_path = ? WHERE id = ?",
            (file_path, doc_id)
        )
        await db_connection.commit()
        return True
    except Exception as e:
        print(f"Ошибка обновления файла: {e}")
        return False


async def delete_document(doc_id: int, user_id: int):
    """Удаление документа"""
    try:
        await db_connection.execute(
            "DELETE FROM documents WHERE id = ? AND user_id = ?",
            (doc_id, user_id)
        )
        await db_connection.commit()
        return True
    except Exception as e:
        print(f"Ошибка удаления документа: {e}")
        return False


async def get_documents_count(user_id: int):
    """Получение количества документов пользователя"""
    try:
        cursor = await db_connection.execute(
            "SELECT COUNT(*) as count FROM documents WHERE user_id = ?",
            (user_id,)
        )
        row = await cursor.fetchone()
        return row["count"] if row else 0
    except Exception as e:
        print(f"Ошибка получения количества: {e}")
        return 0


async def close_db():
    """Закрытие подключения к базе данных"""
    global db_connection
    if db_connection:
        await db_connection.close()
        print("Подключение к базе данных закрыто")
