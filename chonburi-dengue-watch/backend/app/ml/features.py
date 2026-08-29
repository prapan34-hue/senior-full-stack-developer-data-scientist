from datetime import date

import pandas as pd


NUMERIC_FEATURES = [
    "rainfall", "temperature", "humidity", "wind_speed", "previous_cases",
    "week_of_year", "month", "rain_temp_interaction",
]
CATEGORICAL_FEATURES = ["district", "weather_condition"]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def build_features(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    dates = pd.to_datetime(result["record_date"])
    result["week_of_year"] = dates.dt.isocalendar().week.astype(int)
    result["month"] = dates.dt.month
    result["rain_temp_interaction"] = result["rainfall"] * result["temperature"]
    return result[FEATURES]


def row_frame(payload: dict) -> pd.DataFrame:
    payload = payload.copy()
    if isinstance(payload.get("record_date"), date):
        payload["record_date"] = payload["record_date"].isoformat()
    return build_features(pd.DataFrame([payload]))
