import asyncio
import csv
import io
import json
import math
import secrets
from collections import defaultdict
from contextlib import asynccontextmanager
from datetime import datetime, timezone

import joblib
from fastapi import FastAPI, File, Header, HTTPException, Query, UploadFile, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .config import ADMIN_TOKEN, DISTRICTS, MAX_CSV_BYTES, METRICS_PATH, MODEL_PATH, WEATHER_OPTIONS
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


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


@asynccontextmanager
async def lifespan(_: FastAPI):
    global model
    init_db()
    if not MODEL_PATH.exists():
        train_model()
    model = joblib.load(MODEL_PATH)
    yield


app = FastAPI(title="Chonburi Dengue Watch API", version="1.0.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
async def create_observation(payload: ObservationIn):
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
    schedule_dashboard_update()
    return {"id": observation_id, "prediction": result}


@app.delete("/api/observations")
async def reset_observations(x_admin_token: str | None = Header(default=None)):
    if not ADMIN_TOKEN:
        raise HTTPException(503, "data reset is disabled; configure DENGUE_ADMIN_TOKEN on the backend")
    if not x_admin_token or not secrets.compare_digest(x_admin_token, ADMIN_TOKEN):
        raise HTTPException(403, "invalid administrator token")
    with connection() as db:
        deleted_count = db.execute("SELECT COUNT(*) FROM observations").fetchone()[0]
        db.execute("DELETE FROM observations")
    schedule_dashboard_update()
    return {"deleted_count": deleted_count}


@app.get("/api/dashboard")
def dashboard(limit: int = Query(default=80, ge=1, le=500)):
    with connection() as db:
        rows = [dict(row) for row in db.execute("SELECT * FROM observations ORDER BY record_date DESC, district LIMIT ?", (limit,))]
        latest_rows = [dict(row) for row in db.execute("""
            SELECT o.* FROM observations o
            WHERE o.id = (
              SELECT newest.id FROM observations newest
              WHERE newest.district = o.district
              ORDER BY newest.record_date DESC, newest.id DESC LIMIT 1
            )
        """)]
    alerts = sorted(latest_rows, key=lambda item: ({"low": 0, "medium": 1, "high": 2}.get(item["risk_level"], -1), item["predicted_cases"]), reverse=True)
    return {"series": list(reversed(rows)), "alerts": alerts, "summary": {
        "total_cases": sum(item["actual_cases"] for item in latest_rows),
        "predicted_cases": sum(item["predicted_cases"] for item in latest_rows),
        "high_risk_districts": sum(item["risk_level"] == "high" for item in latest_rows),
        "reporting_districts": len(latest_rows),
    }, "updated_at": utc_timestamp()}


connected_websockets: set[WebSocket] = set()


async def broadcast_dashboard_update():
    payload = {"event": "dashboard", "updated_at": utc_timestamp()}
    stale = set()
    for websocket in list(connected_websockets):
        try:
            await websocket.send_json(payload)
        except Exception:
            stale.add(websocket)
    for websocket in stale:
        connected_websockets.discard(websocket)


def schedule_dashboard_update() -> None:
    try:
        asyncio.get_running_loop().create_task(broadcast_dashboard_update())
    except RuntimeError:
        # Sync endpoints run in a worker thread. The polling fallback will refresh
        # clients when no event loop is available to broadcast immediately.
        pass


@app.websocket("/ws")
async def dashboard_ws(websocket: WebSocket):
    await websocket.accept()
    connected_websockets.add(websocket)
    try:
        await websocket.send_json({"event": "dashboard", "updated_at": utc_timestamp()})
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        connected_websockets.discard(websocket)


def clean_csv_record(raw_row):
    clean = {}
    for key, value in raw_row.items():
        if key is None:
            continue
        normalized_key = key.strip().lower().replace(" ", "_")
        normalized_key = normalized_key.replace("-", "_")
        clean[normalized_key] = (value.strip() if isinstance(value, str) else value)

    for key in list(clean.keys()):
        if clean[key] in (None, ""):
            clean[key] = ""

    if "district" not in clean:
        for alt_key in ("location", "area", "subdistrict", "tambon"):
            if alt_key in clean:
                clean["district"] = clean[alt_key]
                break
    if "district" not in clean:
        clean["district"] = "unknown"

    if "record_date" not in clean:
        for alt_key in ("date", "period", "report_date", "observed_date"):
            if alt_key in clean:
                clean["record_date"] = clean[alt_key]
                break

    if "actual_cases" not in clean:
        for alt_key in ("cases", "total_cases", "confirmed_cases", "count"):
            if alt_key in clean:
                clean["actual_cases"] = clean[alt_key]
                break

    return clean


def parse_numeric(value):
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "")
    if not text:
        return 0.0
    number = float(text.removesuffix("%"))
    if not math.isfinite(number):
        raise ValueError("numeric value must be finite")
    return number


@app.post("/api/upload-csv")
async def upload_csv(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, "Only CSV files are supported")

    try:
        content = await file.read(MAX_CSV_BYTES + 1)
        if len(content) > MAX_CSV_BYTES:
            raise HTTPException(413, f"CSV file must not exceed {MAX_CSV_BYTES // (1024 * 1024)} MB")
        text = content.decode("utf-8-sig")
    except HTTPException:
        raise
    except UnicodeDecodeError:
        text = content.decode("latin-1")

    data = io.StringIO(text)
    reader = csv.DictReader(data)
    if reader.fieldnames is None:
        raise HTTPException(400, "CSV file is empty or missing a header row")

    cleaned_rows = []
    invalid_rows = 0
    for row in reader:
        cleaned = clean_csv_record(row)
        if not any((value not in (None, "", " ") for value in cleaned.values())):
            invalid_rows += 1
            continue

        try:
            cleaned["actual_cases"] = parse_numeric(cleaned.get("actual_cases", 0))
            cleaned["rainfall"] = parse_numeric(cleaned.get("rainfall", 0))
            cleaned["temperature"] = parse_numeric(cleaned.get("temperature", 0))
            cleaned["humidity"] = parse_numeric(cleaned.get("humidity", 0))
            actual_cases = cleaned["actual_cases"]
            if actual_cases < 0 or not actual_cases.is_integer():
                raise ValueError("actual_cases must be a non-negative integer")
            if not 0 <= cleaned["rainfall"] <= 1000:
                raise ValueError("rainfall is outside the supported range")
            if not 10 <= cleaned["temperature"] <= 50:
                raise ValueError("temperature is outside the supported range")
            if not 0 <= cleaned["humidity"] <= 100:
                raise ValueError("humidity is outside the supported range")
        except Exception:
            invalid_rows += 1
            continue

        cleaned_rows.append(cleaned)

    if not cleaned_rows:
        raise HTTPException(400, "CSV file contains no valid data rows after cleaning")

    total_cases = sum(int(row.get("actual_cases", 0)) for row in cleaned_rows)

    trend_by_date = defaultdict(float)
    for row in cleaned_rows:
        label = row.get("record_date") or row.get("date") or row.get("period") or "unknown"
        trend_by_date[str(label)] += float(row.get("actual_cases", 0) or 0)

    trend = [{"label": label, "value": int(round(value))} for label, value in sorted(trend_by_date.items())]

    district_totals = defaultdict(float)
    for row in cleaned_rows:
        district = str(row.get("district") or "unknown").strip() or "unknown"
        district_totals[district] += float(row.get("actual_cases", 0) or 0)

    max_cases = max(district_totals.values()) if district_totals else 1
    heatmap = []
    for district, value in sorted(district_totals.items()):
        intensity = min(1.0, value / max_cases) if max_cases else 0
        heatmap.append({
            "district": district,
            "value": int(round(value)),
            "intensity": round(intensity, 3),
            "risk_level": "high" if value >= max_cases * 0.7 else "medium" if value >= max_cases * 0.4 else "low",
        })

    chart_data = []
    for row in cleaned_rows:
        label = row.get("record_date") or row.get("date") or row.get("period") or f"Row {len(chart_data) + 1}"
        value = float(row.get("actual_cases", 0) or 0)
        if value > 0:
            chart_data.append({"label": str(label), "value": int(round(value))})

    return {
        "summary": {
            "total_cases": total_cases,
            "rows": len(cleaned_rows),
            "cleaned_rows": len(cleaned_rows),
            "invalid_rows": invalid_rows,
            "columns": len(reader.fieldnames),
            "fields": reader.fieldnames,
        },
        "preview": cleaned_rows[:10],
        "chart_data": chart_data[:20],
        "analytics": {
            "trend": trend[:20],
            "heatmap": heatmap,
        },
    }
