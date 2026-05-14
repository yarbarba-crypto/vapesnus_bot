import sqlite3
from datetime import datetime


def get_db():
    conn = sqlite3.connect("bot.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            city TEXT,
            registered_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_name TEXT,
            status TEXT DEFAULT 'new',
            city TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)

    conn.commit()
    conn.close()


def add_user(user_id: int, username: str, full_name: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR IGNORE INTO users (user_id, username, full_name, registered_at)
        VALUES (?, ?, ?, ?)
    """, (user_id, username, full_name, datetime.now().isoformat()))
    conn.commit()
    conn.close()


def set_user_city(user_id: int, city: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET city = ? WHERE user_id = ?", (city, user_id))
    conn.commit()
    conn.close()


def get_user(user_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row


def add_order(user_id: int, product_name: str, city: str = None):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO orders (user_id, product_name, status, city, created_at, updated_at)
        VALUES (?, ?, 'new', ?, ?, ?)
    """, (user_id, product_name, city, now, now))
    order_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return order_id


def update_order_status(order_id: int, status: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE orders SET status = ?, updated_at = ? WHERE id = ?
    """, (status, datetime.now().isoformat(), order_id))
    conn.commit()
    conn.close()


def get_user_orders(user_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC LIMIT 10
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_all_users():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    rows = cursor.fetchall()
    conn.close()
    return [row["user_id"] for row in rows]


def get_stats():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM users")
    total_users = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(*) as total FROM orders")
    total_orders = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(*) as total FROM orders WHERE status = 'new'")
    new_orders = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(*) as total FROM orders WHERE status = 'accepted'")
    accepted_orders = cursor.fetchone()["total"]
    conn.close()
    return {
        "total_users": total_users,
        "total_orders": total_orders,
        "new_orders": new_orders,
        "accepted_orders": accepted_orders,
    }
