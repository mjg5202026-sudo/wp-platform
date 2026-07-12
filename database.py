"""
SQLite database layer for the sticky note todo app.
"""

import sqlite3
import os
import datetime


DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "stickynotes.db")


def get_connection() -> sqlite3.Connection:
    """Get a database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """Initialize database tables."""
    conn = get_connection()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS tasks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                content     TEXT    NOT NULL,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
                is_completed INTEGER NOT NULL DEFAULT 0,
                completed_at TEXT
            );

            CREATE TABLE IF NOT EXISTS settings (
                key   TEXT PRIMARY KEY,
                value TEXT
            );
        """)
        conn.commit()
    finally:
        conn.close()


# ── Task operations ──────────────────────────────────────────────

def add_task(content: str) -> int:
    """Add a new task. Returns the new task id."""
    conn = get_connection()
    try:
        cur = conn.execute(
            "INSERT INTO tasks (content) VALUES (?)",
            (content.strip(),)
        )
        conn.commit()
        return cur.lastrowid
    finally:
        conn.close()


def get_active_tasks():
    """Return all uncompleted tasks, ordered by creation time."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, content, created_at FROM tasks WHERE is_completed = 0 ORDER BY created_at ASC"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def complete_task(task_id: int):
    """Mark a task as completed."""
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE tasks SET is_completed = 1, completed_at = datetime('now','localtime') WHERE id = ?",
            (task_id,)
        )
        conn.commit()
    finally:
        conn.close()


def get_completed_tasks():
    """Return completed tasks for history view."""
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT id, content, created_at, completed_at FROM tasks WHERE is_completed = 1 ORDER BY completed_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def restore_task(task_id: int):
    """Restore a completed task back to active list."""
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE tasks SET is_completed = 0, completed_at = NULL WHERE id = ?",
            (task_id,)
        )
        conn.commit()
    finally:
        conn.close()


def delete_task(task_id: int):
    """Permanently delete a task (for history cleanup)."""
    conn = get_connection()
    try:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
    finally:
        conn.close()


# ── Settings operations ──────────────────────────────────────────

def get_setting(key: str, default=None):
    """Get a setting value."""
    conn = get_connection()
    try:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default
    finally:
        conn.close()


def set_setting(key: str, value: str):
    """Set a setting value."""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value)
        )
        conn.commit()
    finally:
        conn.close()
