import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
MODEL_DIR = BASE_DIR / "models"
DB_PATH = Path(os.getenv("DENGUE_DB_PATH", DATA_DIR / "dengue.db"))
MODEL_PATH = MODEL_DIR / "dengue_random_forest.joblib"
METRICS_PATH = MODEL_DIR / "metrics.json"
ADMIN_TOKEN = os.getenv("DENGUE_ADMIN_TOKEN", "")
MAX_CSV_BYTES = 5 * 1024 * 1024

DISTRICTS = [
    "เมืองชลบุรี", "บ้านบึง", "หนองใหญ่", "บางละมุง", "พานทอง",
    "พนัสนิคม", "ศรีราชา", "เกาะสีชัง", "สัตหีบ", "บ่อทอง", "เกาะจันทร์",
]

WEATHER_OPTIONS = ["แจ่มใส", "มีเมฆบางส่วน", "มีเมฆมาก", "ฝนตก", "ฝนฟ้าคะนอง"]
