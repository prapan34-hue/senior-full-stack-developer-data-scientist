from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Integer, Numeric, SmallInteger, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class District(Base):
    __tablename__ = "districts"

    id: Mapped[int] = mapped_column(SmallInteger, primary_key=True)
    code: Mapped[str] = mapped_column(String(10), unique=True, index=True)
    name_th: Mapped[str] = mapped_column(String(100), unique=True)
    name_en: Mapped[str] = mapped_column(String(100), unique=True)
    population_estimate: Mapped[int] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    observations: Mapped[list["WeeklySurveillance"]] = relationship(back_populates="district")


class WeeklySurveillance(Base):
    __tablename__ = "weekly_surveillance"
    __table_args__ = (UniqueConstraint("district_id", "record_date", name="uq_surveillance_district_week"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    district_id: Mapped[int] = mapped_column(ForeignKey("districts.id", ondelete="RESTRICT"), index=True)
    record_date: Mapped[date] = mapped_column(Date, index=True)
    iso_year: Mapped[int] = mapped_column(SmallInteger)
    iso_week: Mapped[int] = mapped_column(SmallInteger)
    weather_condition: Mapped[str] = mapped_column(String(50))
    rainfall_mm: Mapped[Decimal] = mapped_column(Numeric(7, 2))
    temperature_c: Mapped[Decimal] = mapped_column(Numeric(4, 1))
    humidity_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    wind_speed_kmh: Mapped[Decimal] = mapped_column(Numeric(5, 2))
    rainfall_lag_2w_mm: Mapped[Decimal | None] = mapped_column(Numeric(7, 2))
    rainfall_lag_3w_mm: Mapped[Decimal | None] = mapped_column(Numeric(7, 2))
    rainfall_lag_4w_mm: Mapped[Decimal | None] = mapped_column(Numeric(7, 2))
    previous_week_cases: Mapped[int] = mapped_column(Integer, default=0)
    dengue_cases: Mapped[int] = mapped_column(Integer)
    incidence_per_100k: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    synthetic_outbreak_pressure: Mapped[Decimal | None] = mapped_column(Numeric(8, 4))
    source: Mapped[str] = mapped_column(String(30), default="manual")
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    district: Mapped[District] = relationship(back_populates="observations")


class ModelPrediction(Base):
    __tablename__ = "model_predictions"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    surveillance_id: Mapped[int | None] = mapped_column(ForeignKey("weekly_surveillance.id", ondelete="SET NULL"))
    district_id: Mapped[int] = mapped_column(ForeignKey("districts.id", ondelete="RESTRICT"), index=True)
    target_date: Mapped[date] = mapped_column(Date, index=True)
    predicted_cases: Mapped[int] = mapped_column(Integer)
    risk_level: Mapped[str] = mapped_column(String(10))
    model_name: Mapped[str] = mapped_column(String(100))
    model_version: Mapped[str] = mapped_column(String(50))
    feature_snapshot: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
