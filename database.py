# database.py - Модуль для работы с базой данных SQLite

import sqlite3
from sqlite3 import Error
from typing import List, Tuple
import os

# Глобальная переменная для хранения соединения с БД
_connection = None

def initialize(db_file: str = "finance.db") -> None:
    """Инициализация базы данных и создание таблиц"""
    global _connection
    try:
        # Проверяем, существует ли база данных
        is_new_db = not os.path.exists(db_file)
        
        _connection = sqlite3.connect(db_file)
        _create_tables()
        
        # Если база уже существовала, проверяем и добавляем новый столбец
        if not is_new_db:
            _update_schema()
            
        _add_default_categories()
    except Error as e:
        print(f"Ошибка подключения к базе данных: {e}")
        raise

def _update_schema():
    """Обновление схемы базы данных"""
    try:
        # Проверяем, существует ли столбец receipt_path
        cursor = _connection.execute("PRAGMA table_info(transactions)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'receipt_path' not in columns:
            # Добавляем столбец receipt_path
            _connection.execute("ALTER TABLE transactions ADD COLUMN receipt_path TEXT")
            _connection.commit()
    except Error as e:
        print(f"Ошибка обновления схемы базы данных: {e}")
        raise

def _create_tables() -> None:
    """Создание таблиц в базе данных"""
    sql_categories = """
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        type TEXT CHECK(type IN ('income', 'expense'))
    )"""

    sql_transactions = """
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL NOT NULL,
        category_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        description TEXT,
        receipt_path TEXT,
        FOREIGN KEY(category_id) REFERENCES categories(id)
    )"""

    with _connection:
        _connection.execute(sql_categories)
        _connection.execute(sql_transactions)

def add_transaction(amount: float, category_id: int,
                   date: str, description: str = "", receipt_path: str = None) -> None:
    """Добавление новой транзакции"""
    sql = """INSERT INTO transactions(amount, category_id, date, description, receipt_path)
             VALUES(?, ?, ?, ?, ?)"""
    try:
        with _connection:
            _connection.execute(sql, (amount, category_id, date, description, receipt_path))
    except Error as e:
        print(f"Ошибка добавления транзакции: {e}")
        raise

def get_all_transactions() -> List[Tuple]:
    """Получение всех транзакций с дополнительной информацией"""
    sql = """SELECT t.id, t.amount, t.category_id, t.date, t.description, t.receipt_path
             FROM transactions t
             JOIN categories c ON t.category_id = c.id
             ORDER BY t.date DESC"""
    try:
        with _connection:
            cursor = _connection.execute(sql)
            return cursor.fetchall()
    except Error as e:
        print(f"Ошибка получения транзакций: {e}")
        return []

def delete_transaction(transaction_id: int) -> None:
    """Удаление транзакции по ID"""
    sql = "DELETE FROM transactions WHERE id = ?"
    try:
        with _connection:
            _connection.execute(sql, (transaction_id,))
    except Error as e:
        print(f"Ошибка удаления транзакции: {e}")
        raise

def get_category_name(category_id: int) -> str:
    """Получение названия категории по ID"""
    sql = "SELECT name FROM categories WHERE id = ?"
    try:
        with _connection:
            cursor = _connection.execute(sql, (category_id,))
            result = cursor.fetchone()
            return result[0] if result else ""
    except Error as e:
        print(f"Ошибка получения названия категории: {e}")
        return ""

def get_all_categories() -> List[Tuple]:
    """Получение списка всех категорий"""
    sql = "SELECT id, name, type FROM categories ORDER BY name"
    try:
        with _connection:
            cursor = _connection.execute(sql)
            return cursor.fetchall()
    except Error as e:
        print(f"Ошибка получения категорий: {e}")
        return []

def add_category(name: str, category_type: str) -> None:
    """Добавление новой категории"""
    sql = "INSERT INTO categories(name, type) VALUES(?, ?)"
    try:
        with _connection:
            _connection.execute(sql, (name, category_type))
    except Error as e:
        print(f"Ошибка добавления категории: {e}")
        raise

def close_connection() -> None:
    """Закрытие соединения с базой данных"""
    if _connection:
        _connection.close()

def _add_default_categories() -> None:
    """Добавление начальных категорий"""
    default_categories = [
        ("Зарплата", "income"),
        ("Продукты", "expense"),
        ("Коммунальные платежи", "expense"),
        ("Транспорт", "expense"),
        ("Развлечения", "expense"),
        ("Здоровье", "expense"),
        ("Образование", "expense"),
        ("Другое", "expense")
    ]
    
    # Проверяем, есть ли уже категории в базе
    cursor = _connection.execute("SELECT COUNT(*) FROM categories")
    count = cursor.fetchone()[0]
    
    if count == 0:  # Добавляем категории только если таблица пуста
        for name, type in default_categories:
            try:
                add_category(name, type)
            except:
                continue

def update_transaction_date(transaction_id: int, new_date: str) -> None:
    """Обновление даты транзакции"""
    sql = "UPDATE transactions SET date = ? WHERE id = ?"
    try:
        with _connection:
            _connection.execute(sql, (new_date, transaction_id))
    except Error as e:
        print(f"Ошибка обновления даты транзакции: {e}")
        raise

def update_transaction_category(transaction_id: int, new_category_id: int) -> None:
    """Обновление категории транзакции"""
    sql = "UPDATE transactions SET category_id = ? WHERE id = ?"
    try:
        with _connection:
            _connection.execute(sql, (new_category_id, transaction_id))
    except Error as e:
        print(f"Ошибка обновления категории транзакции: {e}")
        raise

def update_transaction_amount(transaction_id: int, new_amount: float) -> None:
    """Обновление суммы транзакции"""
    sql = "UPDATE transactions SET amount = ? WHERE id = ?"
    try:
        with _connection:
            _connection.execute(sql, (new_amount, transaction_id))
    except Error as e:
        print(f"Ошибка обновления суммы транзакции: {e}")
        raise

def update_transaction_description(transaction_id: int, new_description: str) -> None:
    """Обновление описания транзакции"""
    sql = "UPDATE transactions SET description = ? WHERE id = ?"
    try:
        with _connection:
            _connection.execute(sql, (new_description, transaction_id))
    except Error as e:
        print(f"Ошибка обновления описания транзакции: {e}")
        raise

def get_monthly_statistics() -> List[Tuple[int, int, float]]:
    """Получение статистики расходов по месяцам и годам"""
    sql = """
    SELECT 
        CAST(strftime('%Y', date) AS INTEGER) as year,
        CAST(strftime('%m', date) AS INTEGER) as month,
        SUM(amount) as total
    FROM transactions
    JOIN categories ON transactions.category_id = categories.id
    WHERE categories.type = 'expense'
    GROUP BY year, month
    ORDER BY year DESC, month ASC
    """
    try:
        with _connection:
            cursor = _connection.execute(sql)
            return cursor.fetchall()
    except Error as e:
        print(f"Ошибка получения статистики: {e}")
        return []

def update_transaction_receipt(transaction_id: int, receipt_path: str) -> None:
    """Обновление пути к чеку транзакции"""
    sql = "UPDATE transactions SET receipt_path = ? WHERE id = ?"
    try:
        with _connection:
            _connection.execute(sql, (receipt_path, transaction_id))
    except Error as e:
        print(f"Ошибка обновления чека транзакции: {e}")
        raise

# Инициализация начальных категорий при первом запуске
if __name__ == "__main__":
    initialize()
    close_connection()