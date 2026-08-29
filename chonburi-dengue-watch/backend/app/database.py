import sqlite3
from contextlib import contextmanager

from .config import DATA_DIR, DB_PATH


@contextmanager
def connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH)
    db.row_factory = sqlite3.Row
    try:
        yield db
        db.commit()
    finally:
        db.close()


def init_db() -> None:
    with connection() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS observations (
          id INTEGER PRIMARY KEY AUTOINCREMENT, district TEXT NOT NULL,
          record_date TEXT NOT NULL, period_type TEXT NOT NULL,
          actual_cases INTEGER NOT NULL, weather_condition TEXT NOT NULL,
          rainfall REAL NOT NULL, temperature REAL NOT NULL, humidity REAL NOT NULL,
          wind_speed REAL NOT NULL, predicted_cases INTEGER NOT NULL,
          risk_level TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP,
          UNIQUE(district, record_date, period_type)
        );
        """)
