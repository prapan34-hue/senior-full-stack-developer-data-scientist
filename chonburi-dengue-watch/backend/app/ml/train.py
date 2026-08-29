import json

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from ..config import DATA_DIR, DISTRICTS, METRICS_PATH, MODEL_DIR, MODEL_PATH, WEATHER_OPTIONS
from .features import CATEGORICAL_FEATURES, FEATURES, NUMERIC_FEATURES, build_features


def create_mock_data(seed: int = 42, weeks: int = 156) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2023-01-02", periods=weeks, freq="W-MON")
    district_effect = {district: effect for district, effect in zip(DISTRICTS, [8, 3, 1, 10, 4, 5, 8, 1, 5, 2, 2])}
    rows = []
    for district in DISTRICTS:
        previous = max(0, district_effect[district] + rng.poisson(2))
        for current_date in dates:
            season = np.sin(2 * np.pi * (current_date.month - 5) / 12)
            rainfall = max(0, 60 + 55 * season + rng.normal(0, 22))
            temperature = 29.2 + 1.9 * np.sin(2 * np.pi * (current_date.month - 2) / 12) + rng.normal(0, .7)
            humidity = np.clip(68 + rainfall * .11 + rng.normal(0, 5), 45, 98)
            wind = np.clip(8 + rng.normal(0, 2.3), 1, 24)
            weather_idx = 4 if rainfall > 105 else 3 if rainfall > 65 else 2 if humidity > 76 else 1 if rainfall > 18 else 0
            expected = district_effect[district] + .055 * rainfall + .12 * humidity + .32 * previous - .14 * wind + max(0, temperature - 27) * .8
            cases = max(0, int(round(expected + rng.normal(0, 3.2))))
            rows.append({
                "district": district, "record_date": current_date.date().isoformat(),
                "weather_condition": WEATHER_OPTIONS[weather_idx], "rainfall": round(rainfall, 1),
                "temperature": round(temperature, 1), "humidity": round(float(humidity), 1),
                "wind_speed": round(float(wind), 1), "previous_cases": previous,
                "actual_cases": cases,
            })
            previous = cases
    return pd.DataFrame(rows)


def train_model() -> dict:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    data = create_mock_data()
    data.to_csv(DATA_DIR / "mock_dengue_data.csv", index=False, encoding="utf-8-sig")
    split_date = sorted(data["record_date"].unique())[-26]
    train, test = data[data.record_date < split_date], data[data.record_date >= split_date]
    preprocessor = ColumnTransformer([
        ("numeric", "passthrough", NUMERIC_FEATURES),
        ("categorical", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
    ])
    model = Pipeline([
        ("preprocessor", preprocessor),
        ("regressor", RandomForestRegressor(n_estimators=350, max_depth=14, min_samples_leaf=2, random_state=42, n_jobs=-1)),
    ])
    model.fit(build_features(train), train["actual_cases"])
    predictions = model.predict(build_features(test))
    metrics = {
        "algorithm": "RandomForestRegressor", "rows": len(data),
        "train_rows": len(train), "test_rows": len(test),
        "mae": round(float(mean_absolute_error(test["actual_cases"], predictions)), 3),
        "r2": round(float(r2_score(test["actual_cases"], predictions)), 3),
        "split_date": split_date,
        "features": FEATURES,
    }
    joblib.dump(model, MODEL_PATH)
    METRICS_PATH.write_text(json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    return metrics


if __name__ == "__main__":
    print(json.dumps(train_model(), ensure_ascii=False, indent=2))
