from datetime import date
from typing import Literal

from pydantic import BaseModel, Field, field_validator

from .config import DISTRICTS, WEATHER_OPTIONS


class ObservationIn(BaseModel):
    district: str
    record_date: date
    period_type: Literal["weekly", "monthly"] = "weekly"
    actual_cases: int = Field(ge=0, le=10000)
    weather_condition: str
    rainfall: float = Field(ge=0, le=1000)
    temperature: float = Field(ge=10, le=50)
    humidity: float = Field(ge=0, le=100)
    wind_speed: float = Field(ge=0, le=200)

    @field_validator("district")
    @classmethod
    def valid_district(cls, value: str) -> str:
        if value not in DISTRICTS:
            raise ValueError("district must be one of Chonburi's 11 districts")
        return value

    @field_validator("weather_condition")
    @classmethod
    def valid_weather(cls, value: str) -> str:
        if value not in WEATHER_OPTIONS:
            raise ValueError("unsupported weather condition")
        return value


class PredictionIn(BaseModel):
    district: str
    record_date: date
    weather_condition: str
    rainfall: float = Field(ge=0, le=1000)
    temperature: float = Field(ge=10, le=50)
    humidity: float = Field(ge=0, le=100)
    wind_speed: float = Field(ge=0, le=200)
    previous_cases: int = Field(default=0, ge=0, le=10000)

    @field_validator("district")
    @classmethod
    def valid_district(cls, value: str) -> str:
        if value not in DISTRICTS:
            raise ValueError("invalid district")
        return value

    @field_validator("weather_condition")
    @classmethod
    def valid_weather(cls, value: str) -> str:
        if value not in WEATHER_OPTIONS:
            raise ValueError("unsupported weather condition")
        return value


class PredictionOut(BaseModel):
    district: str
    predicted_cases: int
    risk_level: Literal["low", "medium", "high"]
    risk_label: str
    change_percent: float
