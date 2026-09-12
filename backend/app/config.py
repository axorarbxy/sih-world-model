from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
MODEL_DIR = BASE_DIR / "models"
UPLOAD_DIR = BASE_DIR / "data" / "uploads"
DATABASE_URL = f"sqlite:///{BASE_DIR / 'predictions.db'}"
SEQUENCE_LENGTH = 8
FORECAST_STEPS = 5
MODEL_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
