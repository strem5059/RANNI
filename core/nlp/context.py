import json
import sqlite3
from datetime import datetime
from pathlib import Path
from core.utils.logger import ranni_logger

class ContextMemory:
    def __init__(self, db_path=None):
        self.logger = ranni_logger.bind(module="memory")
        if db_path is None:
            db_path = Path(__file__).parent.parent.parent / "data" / "memory.db"
        self.db_path = str(db_path)
        self._init_db()

    def _init_db(self):
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    user_text TEXT,
                    assistant_text TEXT,
                    intent TEXT,
                    metadata TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS context_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    summary TEXT,
                    timestamp TEXT
                )
            """)
            conn.commit()

    def save_interaction(self, user_text, assistant_text, intent="", metadata=None):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO conversations (timestamp, user_text, assistant_text, intent, metadata) VALUES (?, ?, ?, ?, ?)",
                (datetime.now().isoformat(), user_text, assistant_text, intent,
                 json.dumps(metadata or {}))
            )
            conn.commit()

    def get_recent_history(self, limit=10):
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT user_text, assistant_text, intent FROM conversations ORDER BY id DESC LIMIT ?",
                (limit,)
            ).fetchall()
        result = []
        for row in reversed(rows):
            result.append({"user": row[0], "assistant": row[1], "intent": row[2]})
        return result

    def get_context_for_llm(self, limit=5):
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT user_text, assistant_text FROM conversations ORDER BY id DESC LIMIT ?",
                (limit,)
            ).fetchall()
        context = []
        for row in reversed(rows):
            context.append({"role": "user", "content": row[0]})
            context.append({"role": "assistant", "content": row[1]})
        return context

    def clear_history(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM conversations")
            conn.commit()

    def get_stats(self):
        with sqlite3.connect(self.db_path) as conn:
            count = conn.execute("SELECT COUNT(*) FROM conversations").fetchone()[0]
            last = conn.execute("SELECT timestamp, user_text FROM conversations ORDER BY id DESC LIMIT 1").fetchone()
        return {"total_interactions": count, "last_interaction": last}
