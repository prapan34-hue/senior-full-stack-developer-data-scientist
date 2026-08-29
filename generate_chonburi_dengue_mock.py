"""Generate realistic weekly dengue/weather mock data for Chonburi.

The generated data is synthetic and must not be used for real public-health
decisions. It is intended for ML prototyping, UI demos, and pipeline testing.

Usage:
    python generate_chonburi_dengue_mock.py
    python generate_chonburi_dengue_mock.py --start 2023-01-02 --years 3 --seed 42
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class District:
    name_th: str
    name_en: str
    population: int
    urban_factor: float
    coastal_factor: float
    reporting_factor: float


# Population values are deliberately rounded synthetic estimates, not official data.
DISTRICTS = (
    District("เมืองชลบุรี", "Mueang Chonburi", 335_000, 1.18, 0.85, 1.05),
    District("บ้านบึง", "Ban Bueng", 110_000, 0.98, 0.15, 0.98),
    District("หนองใหญ่", "Nong Yai", 25_000, 0.75, 0.05, 0.92),
    District("บางละมุง", "Bang Lamung", 325_000, 1.28, 1.00, 1.08),
    District("พานทอง", "Phan Thong", 85_000, 1.08, 0.15, 1.00),
    District("พนัสนิคม", "Phanat Nikhom", 125_000, 0.94, 0.05, 0.98),
    District("ศรีราชา", "Si Racha", 310_000, 1.25, 0.90, 1.07),
    District("เกาะสีชัง", "Ko Sichang", 5_000, 0.72, 1.20, 0.90),
    District("สัตหีบ", "Sattahip", 175_000, 1.02, 1.00, 1.02),
    District("บ่อทอง", "Bo Thong", 55_000, 0.82, 0.05, 0.94),
    District("เกาะจันทร์", "Ko Chan", 40_000, 0.78, 0.05, 0.93),
)


def sigmoid(value: np.ndarray | float) -> np.ndarray | float:
    return 1.0 / (1.0 + np.exp(-value))


def weather_label(rainfall: float, humidity: float) -> str:
    if rainfall >= 85:
        return "ฝนฟ้าคะนอง"
    if rainfall >= 35:
        return "ฝนตก"
    if humidity >= 78:
        return "มีเมฆมาก"
    if rainfall >= 8:
        return "มีเมฆบางส่วน"
    return "แจ่มใส"


def outbreak_pressure(
    rng: np.random.Generator, n_weeks: int, n_districts: int
) -> np.ndarray:
    """Create occasional province-wide and district-specific outbreak waves."""
    pressure = np.zeros((n_weeks, n_districts), dtype=float)
    years = max(1, int(np.ceil(n_weeks / 52)))

    # A province-wide wave typically occurs in or shortly after the rainy season.
    for year in range(years):
        center = min(n_weeks - 1, year * 52 + int(rng.integers(27, 41)))
        width = float(rng.uniform(3.5, 7.5))
        magnitude = float(rng.uniform(0.10, 0.45))
        timeline = np.arange(n_weeks)
        common_wave = magnitude * np.exp(-0.5 * ((timeline - center) / width) ** 2)
        pressure += common_wave[:, None]

        # Two to four districts receive an additional local cluster.
        selected = rng.choice(n_districts, size=int(rng.integers(2, 5)), replace=False)
        for district_idx in selected:
            local_center = int(np.clip(center + rng.integers(-3, 4), 0, n_weeks - 1))
            local_width = float(rng.uniform(2.0, 5.0))
            local_size = float(rng.uniform(0.10, 0.35))
            pressure[:, district_idx] += local_size * np.exp(
                -0.5 * ((timeline - local_center) / local_width) ** 2
            )
    return pressure


def generate_mock_data(
    start_date: str = "2023-01-02", years: int = 3, seed: int = 42
) -> pd.DataFrame:
    """Return one row per district per epidemiological week."""
    if years < 1:
        raise ValueError("years must be at least 1")

    rng = np.random.default_rng(seed)
    n_weeks = years * 52
    dates = pd.date_range(start=start_date, periods=n_weeks, freq="W-MON")
    n_districts = len(DISTRICTS)

    # Province-level weather ensures neighboring districts move together.
    week = np.arange(n_weeks)
    seasonal_rain = 55 + 58 * np.sin(2 * np.pi * (week - 17) / 52)
    monsoon_pulse = 35 * np.maximum(0, np.sin(2 * np.pi * (week - 20) / 52))
    province_rain = np.maximum(0, seasonal_rain + monsoon_pulse + rng.gamma(2.0, 9.0, n_weeks) - 12)
    province_temp = 28.9 + 2.2 * np.sin(2 * np.pi * (week - 7) / 52) + rng.normal(0, 0.45, n_weeks)
    province_humidity = np.clip(66 + 0.13 * province_rain + rng.normal(0, 2.8, n_weeks), 48, 96)
    province_wind = np.clip(7.5 + 1.8 * np.sin(2 * np.pi * (week - 18) / 52) + rng.normal(0, 1.1, n_weeks), 1, 22)
    outbreak = outbreak_pressure(rng, n_weeks, n_districts)

    all_rows: list[dict] = []
    for district_idx, district in enumerate(DISTRICTS):
        # Coastal areas are windier and slightly cooler; inland areas retain more rain.
        local_rain = np.maximum(
            0,
            province_rain * (0.90 + 0.08 * district.coastal_factor)
            + rng.normal(0, 13, n_weeks),
        )
        local_temp = np.clip(
            province_temp - 0.35 * district.coastal_factor + rng.normal(0, 0.35, n_weeks),
            22,
            38,
        )
        local_humidity = np.clip(
            province_humidity + 2.2 * district.coastal_factor + rng.normal(0, 2.2, n_weeks),
            45,
            99,
        )
        local_wind = np.clip(
            province_wind + 2.8 * district.coastal_factor + rng.normal(0, 1.0, n_weeks),
            1,
            28,
        )

        cases = np.zeros(n_weeks, dtype=int)
        previous_cases = max(0, int(rng.poisson(1 + district.population / 90_000)))

        for t, current_date in enumerate(dates):
            # Mosquito abundance reacts after accumulated rainfall, not instantly.
            rain_lag_2 = local_rain[max(0, t - 2)]
            rain_lag_3 = local_rain[max(0, t - 3)]
            rain_lag_4 = local_rain[max(0, t - 4)]
            weighted_lagged_rain = 0.25 * rain_lag_2 + 0.50 * rain_lag_3 + 0.25 * rain_lag_4

            # Dengue suitability peaks around 28-30 C and high humidity.
            temp_suitability = np.exp(-((local_temp[t] - 29.0) / 4.2) ** 2)
            humidity_suitability = sigmoid((local_humidity[t] - 68.0) / 7.0)
            rain_suitability = sigmoid((weighted_lagged_rain - 35.0) / 19.0)

            # Population controls scale; urban density and previous infections add persistence.
            baseline = district.population / 100_000 * 0.65
            vector_pressure = (
                district.population
                / 100_000
                * district.urban_factor
                * 4.6
                * rain_suitability
                * temp_suitability
                * humidity_suitability
            )
            autoregressive = 0.34 * previous_cases
            outbreak_extra = (
                district.population / 100_000 * 8.0 * outbreak[t, district_idx]
            )
            expected_cases = max(
                0.05,
                (baseline + vector_pressure + autoregressive + outbreak_extra)
                * district.reporting_factor,
            )

            # Negative binomial-like overdispersion: surveillance counts vary more than Poisson.
            dispersion = 4.5
            probability = dispersion / (dispersion + expected_cases)
            reported_cases = int(rng.negative_binomial(dispersion, probability))
            cases[t] = reported_cases

            iso = current_date.isocalendar()
            all_rows.append(
                {
                    "district_th": district.name_th,
                    "district_en": district.name_en,
                    "record_date": current_date.date().isoformat(),
                    "iso_year": int(iso.year),
                    "iso_week": int(iso.week),
                    "population_estimate": district.population,
                    "weather_condition": weather_label(local_rain[t], local_humidity[t]),
                    "rainfall_mm": round(float(local_rain[t]), 1),
                    "temperature_c": round(float(local_temp[t]), 1),
                    "humidity_pct": round(float(local_humidity[t]), 1),
                    "wind_speed_kmh": round(float(local_wind[t]), 1),
                    "rainfall_lag_2w_mm": round(float(rain_lag_2), 1),
                    "rainfall_lag_3w_mm": round(float(rain_lag_3), 1),
                    "rainfall_lag_4w_mm": round(float(rain_lag_4), 1),
                    "previous_week_cases": previous_cases,
                    "dengue_cases": reported_cases,
                    "incidence_per_100k": round(reported_cases / district.population * 100_000, 2),
                    "synthetic_outbreak_pressure": round(float(outbreak[t, district_idx]), 4),
                }
            )
            previous_cases = reported_cases

    return pd.DataFrame(all_rows).sort_values(["record_date", "district_th"]).reset_index(drop=True)


def validate_data(frame: pd.DataFrame, years: int) -> None:
    expected_rows = len(DISTRICTS) * years * 52
    if len(frame) != expected_rows:
        raise RuntimeError(f"expected {expected_rows} rows, found {len(frame)}")
    if frame.isna().any().any():
        raise RuntimeError("generated data contains missing values")
    if (frame[["rainfall_mm", "wind_speed_kmh", "dengue_cases"]] < 0).any().any():
        raise RuntimeError("generated data contains negative values")
    if frame["district_th"].nunique() != 11:
        raise RuntimeError("data must contain all 11 districts")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", default="2023-01-02", help="First Monday (YYYY-MM-DD)")
    parser.add_argument("--years", type=int, default=3)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", type=Path, default=Path("chonburi_dengue_mock_3y.csv"))
    args = parser.parse_args()

    data = generate_mock_data(args.start, args.years, args.seed)
    validate_data(data, args.years)
    data.to_csv(args.output, index=False, encoding="utf-8-sig")

    print(f"Saved: {args.output.resolve()}")
    print(f"Rows: {len(data):,} | Districts: {data['district_th'].nunique()}")
    print(f"Date range: {data['record_date'].min()} to {data['record_date'].max()}")
    print(f"Total synthetic cases: {data['dengue_cases'].sum():,}")
    print("\nCases by district:")
    print(data.groupby("district_th")["dengue_cases"].agg(["sum", "mean", "max"]).round(2))


if __name__ == "__main__":
    main()
