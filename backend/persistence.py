import os
import sqlite3
from datetime import datetime, timezone

_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
FEEDBACK_DB_PATH = os.path.abspath(os.path.join(_DATA_DIR, "feedback.db"))

_feedback_conn: sqlite3.Connection | None = None


def _get_feedback_conn() -> sqlite3.Connection:
    global _feedback_conn
    if _feedback_conn is None:
        os.makedirs(_DATA_DIR, exist_ok=True)
        _feedback_conn = sqlite3.connect(FEEDBACK_DB_PATH, check_same_thread=False)
        _feedback_conn.execute(
            """
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id TEXT NOT NULL,
                rating TEXT NOT NULL,
                reward_signal REAL NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        _feedback_conn.commit()
    return _feedback_conn


def log_feedback(customer_id: str, rating: str) -> float:
    reward_signal = 1.0 if rating == "like" else -1.0
    conn = _get_feedback_conn()
    conn.execute(
        "INSERT INTO feedback (customer_id, rating, reward_signal, created_at) VALUES (?, ?, ?, ?)",
        (customer_id, rating, reward_signal, datetime.now(timezone.utc).isoformat()),
    )
    conn.commit()
    return reward_signal


def get_feedback_summary() -> dict:
    conn = _get_feedback_conn()
    rows = conn.execute(
        "SELECT rating, COUNT(*) FROM feedback GROUP BY rating"
    ).fetchall()
    counts = {rating: count for rating, count in rows}
    likes = counts.get("like", 0)
    dislikes = counts.get("dislike", 0)
    total = likes + dislikes
    return {
        "total": total,
        "likes": likes,
        "dislikes": dislikes,
        "like_rate_percent": round((likes / total) * 100, 1) if total else 0.0,
    }
