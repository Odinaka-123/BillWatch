import hashlib
import sqlite3
from pathlib import Path

DB_PATH = Path("data/auth.db")
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def init_auth_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'inspector',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def create_user(username: str, password: str, role: str = "inspector") -> bool:
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, hash_password(password), role)
        )
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False


def verify_user(username: str, password: str) -> dict | None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.execute(
        "SELECT id, username, role FROM users WHERE username=? AND password=?",
        (username, hash_password(password))
    )
    row = cursor.fetchone()
    conn.close()
    if row:
        return {"id": row[0], "username": row[1], "role": row[2]}
    return None