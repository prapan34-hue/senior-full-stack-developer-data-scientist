from contextlib import asynccontextmanager
from datetime import date

from fastapi import Depends, FastAPI, HTTPException, Query, status
from sqlalchemy import select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from .database import engine, get_db
from .models import District, WeeklySurveillance
from .schemas import DistrictRead, SurveillanceCreate, SurveillanceRead


@asynccontextmanager
async def lifespan(_: FastAPI):
    # schema.sql/Alembic should create tables; the app only verifies connectivity.
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))
    yield
    await engine.dispose()


app = FastAPI(title="Chonburi Dengue PostgreSQL API", version="1.0.0", lifespan=lifespan)


@app.get("/api/health")
async def health(db: AsyncSession = Depends(get_db)):
    await db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}


@app.get("/api/districts", response_model=list[DistrictRead])
async def list_districts(db: AsyncSession = Depends(get_db)):
    result = await db.scalars(select(District).where(District.is_active.is_(True)).order_by(District.id))
    return list(result)


@app.post("/api/surveillance", response_model=SurveillanceRead, status_code=status.HTTP_201_CREATED)
async def create_surveillance(payload: SurveillanceCreate, db: AsyncSession = Depends(get_db)):
    district = await db.scalar(select(District).where(District.code == payload.district_code, District.is_active.is_(True)))
    if district is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "district not found")

    iso = payload.record_date.isocalendar()
    incidence = round(payload.dengue_cases / district.population_estimate * 100_000, 2)
    row = WeeklySurveillance(
        district_id=district.id,
        record_date=payload.record_date,
        iso_year=iso.year,
        iso_week=iso.week,
        weather_condition=payload.weather_condition,
        rainfall_mm=payload.rainfall_mm,
        temperature_c=payload.temperature_c,
        humidity_pct=payload.humidity_pct,
        wind_speed_kmh=payload.wind_speed_kmh,
        rainfall_lag_2w_mm=payload.rainfall_lag_2w_mm,
        rainfall_lag_3w_mm=payload.rainfall_lag_3w_mm,
        rainfall_lag_4w_mm=payload.rainfall_lag_4w_mm,
        previous_week_cases=payload.previous_week_cases,
        dengue_cases=payload.dengue_cases,
        incidence_per_100k=incidence,
        synthetic_outbreak_pressure=payload.synthetic_outbreak_pressure,
        source=payload.source,
        notes=payload.notes,
    )
    db.add(row)
    try:
        await db.flush()
        await db.refresh(row)
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(status.HTTP_409_CONFLICT, "data for this district and week already exists") from exc
    return row


@app.get("/api/surveillance", response_model=list[SurveillanceRead])
async def list_surveillance(
    district_code: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    query = select(WeeklySurveillance).join(District)
    if district_code:
        query = query.where(District.code == district_code)
    if date_from:
        query = query.where(WeeklySurveillance.record_date >= date_from)
    if date_to:
        query = query.where(WeeklySurveillance.record_date <= date_to)
    query = query.order_by(WeeklySurveillance.record_date.desc(), WeeklySurveillance.district_id).limit(limit).offset(offset)
    result = await db.scalars(query)
    return list(result)


@app.get("/api/surveillance/{record_id}", response_model=SurveillanceRead)
async def get_surveillance(record_id: int, db: AsyncSession = Depends(get_db)):
    row = await db.get(WeeklySurveillance, record_id)
    if row is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "record not found")
    return row
