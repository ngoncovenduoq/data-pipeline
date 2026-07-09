"""Transform: chuyen du lieu tu staging sang star schema (dw)."""
import logging
from pathlib import Path

from etl.load import get_conn

logger = logging.getLogger(__name__)

DDL_PATH = Path(__file__).resolve().parent.parent / "sql" / "02_star_schema.sql"

TRANSFORM_SQL = """
-- 1. Cap nhat dim_city
INSERT INTO dw.dim_city (city_name)
SELECT DISTINCT city FROM staging.weather
UNION
SELECT DISTINCT city FROM staging.air_quality
ON CONFLICT (city_name) DO NOTHING;

-- 2. Cap nhat dim_time
INSERT INTO dw.dim_time (ts, date, hour, day_of_week, is_weekend)
SELECT DISTINCT measured_at,
       measured_at::date,
       EXTRACT(HOUR FROM measured_at)::int,
       EXTRACT(ISODOW FROM measured_at)::int,
       EXTRACT(ISODOW FROM measured_at) IN (6, 7)
FROM (
    SELECT measured_at FROM staging.weather
    UNION
    SELECT measured_at FROM staging.air_quality
) t
ON CONFLICT (ts) DO NOTHING;

-- 3. Fact: thoi tiet
INSERT INTO dw.fact_weather (city_key, time_key, temp_c, humidity, wind_speed_ms, weather)
SELECT c.city_key, t.time_key, s.temp_c, s.humidity, s.wind_speed_ms, s.weather
FROM staging.weather s
JOIN dw.dim_city c ON c.city_name = s.city
JOIN dw.dim_time t ON t.ts = s.measured_at
ON CONFLICT (city_key, time_key) DO NOTHING;

-- 4. Fact: chat luong khong khi
INSERT INTO dw.fact_air_quality (city_key, time_key, pm25, pm10, station, source)
SELECT c.city_key, t.time_key, s.pm25, s.pm10, s.station, s.source
FROM staging.air_quality s
JOIN dw.dim_city c ON c.city_name = s.city
JOIN dw.dim_time t ON t.ts = s.measured_at
ON CONFLICT (city_key, time_key) DO NOTHING;
"""


def transform() -> None:
    """Chay DDL (neu chua co bang) roi incremental load staging -> dw."""
    with get_conn() as conn, conn.cursor() as cur:
        cur.execute(DDL_PATH.read_text())
        cur.execute(TRANSFORM_SQL)
    logger.info("Transform staging -> dw completed")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    transform()
