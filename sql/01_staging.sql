CREATE SCHEMA IF NOT EXISTS staging;

CREATE TABLE IF NOT EXISTS staging.weather (
    id            SERIAL PRIMARY KEY,
    city          TEXT NOT NULL,
    temp_c        NUMERIC,
    humidity      INT,
    wind_speed_ms NUMERIC,
    weather       TEXT,
    measured_at   TIMESTAMP NOT NULL,
    loaded_at     TIMESTAMP DEFAULT now(),
    UNIQUE (city, measured_at)          -- chan duplicate khi chay lai
);

CREATE TABLE IF NOT EXISTS staging.air_quality (
    id          SERIAL PRIMARY KEY,
    city        TEXT NOT NULL,
    station     TEXT,
    pm25        NUMERIC,
    pm10        NUMERIC,
    source      TEXT,
    measured_at TIMESTAMP NOT NULL,
    loaded_at   TIMESTAMP DEFAULT now(),
    UNIQUE (city, measured_at)
);
