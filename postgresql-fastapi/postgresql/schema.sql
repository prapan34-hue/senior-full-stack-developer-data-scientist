BEGIN;

CREATE TABLE IF NOT EXISTS districts (
    id              SMALLINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    code            VARCHAR(10)  NOT NULL UNIQUE,
    name_th         VARCHAR(100) NOT NULL UNIQUE,
    name_en         VARCHAR(100) NOT NULL UNIQUE,
    population_estimate INTEGER NOT NULL CHECK (population_estimate > 0),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS weekly_surveillance (
    id                          BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    district_id                 SMALLINT NOT NULL REFERENCES districts(id)
                                    ON UPDATE CASCADE ON DELETE RESTRICT,
    record_date                 DATE NOT NULL,
    iso_year                    SMALLINT NOT NULL CHECK (iso_year BETWEEN 2000 AND 2200),
    iso_week                    SMALLINT NOT NULL CHECK (iso_week BETWEEN 1 AND 53),
    weather_condition           VARCHAR(50) NOT NULL CHECK (
        weather_condition IN ('แจ่มใส', 'มีเมฆบางส่วน', 'มีเมฆมาก', 'ฝนตก', 'ฝนฟ้าคะนอง')
    ),
    rainfall_mm                 NUMERIC(7,2) NOT NULL CHECK (rainfall_mm BETWEEN 0 AND 2000),
    temperature_c               NUMERIC(4,1) NOT NULL CHECK (temperature_c BETWEEN 10 AND 50),
    humidity_pct                NUMERIC(5,2) NOT NULL CHECK (humidity_pct BETWEEN 0 AND 100),
    wind_speed_kmh              NUMERIC(5,2) NOT NULL CHECK (wind_speed_kmh BETWEEN 0 AND 300),
    rainfall_lag_2w_mm          NUMERIC(7,2) CHECK (rainfall_lag_2w_mm BETWEEN 0 AND 2000),
    rainfall_lag_3w_mm          NUMERIC(7,2) CHECK (rainfall_lag_3w_mm BETWEEN 0 AND 2000),
    rainfall_lag_4w_mm          NUMERIC(7,2) CHECK (rainfall_lag_4w_mm BETWEEN 0 AND 2000),
    previous_week_cases         INTEGER NOT NULL DEFAULT 0 CHECK (previous_week_cases >= 0),
    dengue_cases                INTEGER NOT NULL CHECK (dengue_cases >= 0),
    incidence_per_100k          NUMERIC(10,2) NOT NULL CHECK (incidence_per_100k >= 0),
    synthetic_outbreak_pressure NUMERIC(8,4),
    source                      VARCHAR(30) NOT NULL DEFAULT 'manual' CHECK (
        source IN ('manual', 'csv_import', 'api', 'synthetic')
    ),
    notes                       TEXT,
    created_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at                  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_surveillance_district_week UNIQUE (district_id, record_date),
    CONSTRAINT ck_record_date_monday CHECK (EXTRACT(ISODOW FROM record_date) = 1)
);

CREATE TABLE IF NOT EXISTS model_predictions (
    id                 BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    surveillance_id    BIGINT REFERENCES weekly_surveillance(id) ON DELETE SET NULL,
    district_id        SMALLINT NOT NULL REFERENCES districts(id) ON DELETE RESTRICT,
    target_date        DATE NOT NULL,
    predicted_cases    INTEGER NOT NULL CHECK (predicted_cases >= 0),
    risk_level         VARCHAR(10) NOT NULL CHECK (risk_level IN ('low', 'medium', 'high')),
    model_name         VARCHAR(100) NOT NULL,
    model_version      VARCHAR(50) NOT NULL,
    feature_snapshot   JSONB NOT NULL DEFAULT '{}'::JSONB,
    created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_prediction_version UNIQUE (district_id, target_date, model_name, model_version)
);

CREATE INDEX IF NOT EXISTS ix_surveillance_record_date
    ON weekly_surveillance (record_date DESC);
CREATE INDEX IF NOT EXISTS ix_surveillance_district_date
    ON weekly_surveillance (district_id, record_date DESC);
CREATE INDEX IF NOT EXISTS ix_surveillance_high_cases
    ON weekly_surveillance (dengue_cases DESC, record_date DESC);
CREATE INDEX IF NOT EXISTS ix_predictions_target_risk
    ON model_predictions (target_date DESC, risk_level);
CREATE INDEX IF NOT EXISTS ix_predictions_features_gin
    ON model_predictions USING GIN (feature_snapshot);

INSERT INTO districts (code, name_th, name_en, population_estimate) VALUES
    ('CH01', 'เมืองชลบุรี', 'Mueang Chonburi', 335000),
    ('CH02', 'บ้านบึง', 'Ban Bueng', 110000),
    ('CH03', 'หนองใหญ่', 'Nong Yai', 25000),
    ('CH04', 'บางละมุง', 'Bang Lamung', 325000),
    ('CH05', 'พานทอง', 'Phan Thong', 85000),
    ('CH06', 'พนัสนิคม', 'Phanat Nikhom', 125000),
    ('CH07', 'ศรีราชา', 'Si Racha', 310000),
    ('CH08', 'เกาะสีชัง', 'Ko Sichang', 5000),
    ('CH09', 'สัตหีบ', 'Sattahip', 175000),
    ('CH10', 'บ่อทอง', 'Bo Thong', 55000),
    ('CH11', 'เกาะจันทร์', 'Ko Chan', 40000)
ON CONFLICT (code) DO UPDATE SET
    name_th = EXCLUDED.name_th,
    name_en = EXCLUDED.name_en,
    population_estimate = EXCLUDED.population_estimate,
    updated_at = NOW();

COMMIT;
