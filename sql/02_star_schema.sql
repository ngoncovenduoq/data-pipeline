CREATE SCHEMA IF NOT EXISTS dw;

CREATE TABLE IF NOT EXISTS dw.dim_city (
    city_key  SERIAL PRIMARY KEY,
    city_name TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS dw.dim_time (
    time_key    SERIAL PRIMARY KEY,
    ts          TIMESTAMP UNIQUE NOT NULL,
    date        DATE NOT NULL,
    hour        INT NOT NULL,
    day_of_week INT NOT NULL,      -- 1=Thu 2 ... 7=Chu nhat
    is_weekend  BOOLEAN NOT NULL
);

CREATE TABLE IF NOT EXISTS dw.fact_weather (
    city_key      INT NOT NULL REFERENCES dw.dim_city(city_key),
    time_key      INT NOT NULL REFERENCES dw.dim_time(time_key),
    temp_c        NUMERIC,
    humidity      INT,
    wind_speed_ms NUMERIC,
    weather       TEXT,
    PRIMARY KEY (city_key, time_key)
);

CREATE TABLE IF NOT EXISTS dw.fact_air_quality (
    city_key INT NOT NULL REFERENCES dw.dim_city(city_key),
    time_key INT NOT NULL REFERENCES dw.dim_time(time_key),
    pm25     NUMERIC,
    pm10     NUMERIC,
    station  TEXT,
    source   TEXT,
    PRIMARY KEY (city_key, time_key)
);
