import json
from contextlib import asynccontextmanager

import joblib
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .config import DISTRICTS, METRICS_PATH, MODEL_PATH, WEATHER_OPTIONS
from .database import connection, init_db
from .ml.features import row_frame
from .ml.train import train_model
from .schemas import ObservationIn, PredictionIn, PredictionOut

model = None


def risk_for(predicted: int, previous: int) -> tuple[str, str, float]:
    change = ((predicted - previous) / max(previous, 1)) * 100
    if predicted >= 30 or (predicted >= 15 and change >= 40):
        return "high", "เสี่ยงสูง", round(change, 1)
    if predicted >= 15 or change >= 20:
        return "medium", "เฝ้าระวัง", round(change, 1)
    return "low", "ปกติ", round(change, 1)


def predict(payload: PredictionIn) -> PredictionOut:
    if model is None:
        raise HTTPException(503, "model is not available")
    value = max(0, int(round(float(model.predict(row_frame(payload.model_dump()))[0]))))
    level, label, change = risk_for(value, payload.previous_cases)
    return PredictionOut(district=payload.district, predicted_cases=value, risk_level=level, risk_label=label, change_percent=change)


@asynccontextmanager
async def lifespan(_: FastAPI):
    global model
    init_db()
    if not MODEL_PATH.exists():
        train_model()
    model = joblib.load(MODEL_PATH)
    yield


app = FastAPI(title="Chonburi Dengue Watch API", version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])


@app.get("/api/health")
def health():
    return {"status": "ok", "model_ready": model is not None}


@app.get("/api/config")
def config():
    metrics = json.loads(METRICS_PATH.read_text(encoding="utf-8")) if METRICS_PATH.exists() else {}
    return {"districts": DISTRICTS, "weather_options": WEATHER_OPTIONS, "model_metrics": metrics}


@app.post("/api/predict", response_model=PredictionOut)
def prediction(payload: PredictionIn):
    return predict(payload)


@app.post("/api/observations", status_code=201)
def create_observation(payload: ObservationIn):
    prediction_payload = PredictionIn(**payload.model_dump(exclude={"period_type", "actual_cases"}), previous_cases=payload.actual_cases)
    result = predict(prediction_payload)
    try:
        with connection() as db:
            cursor = db.execute("""
              INSERT INTO observations (district, record_date, period_type, actual_cases, weather_condition,
                rainfall, temperature, humidity, wind_speed, predicted_cases, risk_level)
              VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (payload.district, payload.record_date.isoformat(), payload.period_type, payload.actual_cases,
                  payload.weather_condition, payload.rainfall, payload.temperature, payload.humidity,
                  payload.wind_speed, result.predicted_cases, result.risk_level))
            observation_id = cursor.lastrowid
    except Exception as exc:
        if "UNIQUE" in str(exc):
            raise HTTPException(409, "observation already exists for this period") from exc
        raise
    return {"id": observation_id, "prediction": result}


@app.get("/api/dashboard")
def dashboard(limit: int = Query(default=80, ge=1, le=500)):
    with connection() as db:
        rows = [dict(row) for row in db.execute("SELECT * FROM observations ORDER BY record_date DESC, district LIMIT ?", (limit,))]
    latest = {}
    for row in rows:
        latest.setdefault(row["district"], row)
    alerts = sorted(latest.values(), key=lambda item: (item["risk_level"] == "high", item["predicted_cases"]), reverse=True)
    return {"series": list(reversed(rows)), "alerts": alerts, "summary": {
        "total_cases": sum(item["actual_cases"] for item in latest.values()),
        "predicted_cases": sum(item["predicted_cases"] for item in latest.values()),
        "high_risk_districts": sum(item["risk_level"] == "high" for item in latest.values()),
        "reporting_districts": len(latest),
    }}
