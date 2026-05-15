import os
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "")


def get_db():
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor, sslmode='require')
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            registered_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            product_name TEXT,
            status TEXT DEFAULT 'new',
            city TEXT,
            created_at TEXT,
            updated_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blocked_users (
            user_id BIGINT PRIMARY KEY,
            reason TEXT,
            blocked_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id SERIAL PRIMARY KEY,
            user_id BIGINT,
            action TEXT,
            details TEXT,
            created_at TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS rate_limit (
            user_id BIGINT PRIMARY KEY,
            requests INTEGER DEFAULT 0,
            window_start TEXT
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()


def add_user(user_id: int, username: str, full_name: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (user_id, username, full_name, registered_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (user_id) DO NOTHING
    """, (user_id, username, full_name, datetime.now().isoformat()))
    conn.commit()
    cursor.close()
    conn.close()


def get_user(user_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def add_order(user_id: int, product_name: str, city: str = None):
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO orders (user_id, product_name, status, city, created_at, updated_at)
        VALUES (%s, %s, 'new', %s, %s, %s)
        RETURNING id
    """, (user_id, product_name, city, now, now))
    order_id = cursor.fetchone()["id"]
    conn.commit()
    cursor.close()
    conn.close()
    return order_id


def update_order_status(order_id: int, status: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE orders SET status = %s, updated_at = %s WHERE id = %s
    """, (status, datetime.now().isoformat(), order_id))
    conn.commit()
    cursor.close()
    conn.close()


def get_user_orders(user_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM orders WHERE user_id = %s ORDER BY created_at DESC LIMIT 10
    """, (user_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_all_users():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users")
    rows = cursor.fetchall()
    cursor.close()
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
    cursor.close()
    conn.close()
    return {
        "total_users": total_users,
        "total_orders": total_orders,
        "new_orders": new_orders,
        "accepted_orders": accepted_orders,
    }


def is_blocked(user_id: int) -> bool:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM blocked_users WHERE user_id = %s", (user_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row is not None


def block_user(user_id: int, reason: str = ""):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO blocked_users (user_id, reason, blocked_at)
        VALUES (%s, %s, %s)
        ON CONFLICT (user_id) DO UPDATE SET reason = %s
    """, (user_id, reason, datetime.now().isoformat(), reason))
    conn.commit()
    cursor.close()
    conn.close()


def unblock_user(user_id: int):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM blocked_users WHERE user_id = %s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()


def add_log(user_id: int, action: str, details: str = ""):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO logs (user_id, action, details, created_at)
        VALUES (%s, %s, %s, %s)
    """, (user_id, action, details, datetime.now().isoformat()))
    conn.commit()
    cursor.close()
    conn.close()


def check_rate_limit(user_id: int, max_requests: int = 10) -> bool:
    conn = get_db()
    cursor = conn.cursor()
    now = datetime.now()

    cursor.execute("SELECT * FROM rate_limit WHERE user_id = %s", (user_id,))
    row = cursor.fetchone()

    if not row:
        cursor.execute("""
            INSERT INTO rate_limit (user_id, requests, window_start)
            VALUES (%s, 1, %s)
        """, (user_id, now.isoformat()))
        conn.commit()
        cursor.close()
        conn.close()
        return True

    window_start = datetime.fromisoformat(row["window_start"])
    diff = (now - window_start).total_seconds()

    if diff > 60:
        cursor.execute("""
            UPDATE rate_limit SET requests = 1, window_start = %s WHERE user_id = %s
        """, (now.isoformat(), user_id))
        conn.commit()
        cursor.close()
        conn.close()
        return True

    if row["requests"] >= max_requests:
        cursor.close()
        conn.close()
        return False

    cursor.execute("""
        UPDATE rate_limit SET requests = requests + 1 WHERE user_id = %s
    """, (user_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return True
