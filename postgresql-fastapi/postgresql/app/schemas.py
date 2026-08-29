from datetime import date, datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


Weather = Literal["แจ่มใส", "มีเมฆบางส่วน", "มีเมฆมาก", "ฝนตก", "ฝนฟ้าคะนอง"]


class SurveillanceCreate(BaseModel):
    district_code: str = Field(min_length=4, max_length=10)
    record_date: date
    weather_condition: Weather
    rainfall_mm: Decimal = Field(ge=0, le=2000)
    temperature_c: Decimal = Field(ge=10, le=50)
    humidity_pct: Decimal = Field(ge=0, le=100)
    wind_speed_kmh: Decimal = Field(ge=0, le=300)
    rainfall_lag_2w_mm: Decimal | None = Field(default=None, ge=0, le=2000)
    rainfall_lag_3w_mm: Decimal | None = Field(default=None, ge=0, le=2000)
    rainfall_lag_4w_mm: Decimal | None = Field(default=None, ge=0, le=2000)
    previous_week_cases: int = Field(default=0, ge=0)
    dengue_cases: int = Field(ge=0)
    source: Literal["manual", "csv_import", "api", "synthetic"] = "manual"
    synthetic_outbreak_pressure: Decimal | None = None
    notes: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def require_monday(self):
        if self.record_date.weekday() != 0:
            raise ValueError("record_date must be a Monday")
        return self


class SurveillanceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    district_id: int
    record_date: date
    iso_year: int
    iso_week: int
    weather_condition: str
    rainfall_mm: Decimal
    temperature_c: Decimal
    humidity_pct: Decimal
    wind_speed_kmh: Decimal
    previous_week_cases: int
    dengue_cases: int
    incidence_per_100k: Decimal
    source: str
    created_at: datetime


class DistrictRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name_th: str
    name_en: str
    population_estimate: int
