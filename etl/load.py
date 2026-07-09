"""Load: ghi du lieu da validate vao PostgreSQL (schema staging)."""
import logging
import os
from datetime import datetime, timezone

import psycopg2
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)


def get_conn():
    return psycopg2.connect(
        host=os.getenv("DW_HOST", "localhost"),
        port=os.getenv("DW_PORT", "5433"),
        dbname=os.getenv("DW_DB"),
        user=os.getenv("DW_USER"),
        password=os.getenv("DW_PASSWORD"),
    )


WEATHER_SQL = """
INSERT INTO staging.weather (city, temp_c, humidity, wind_speed_ms, weather, measured_at)
VALUES (%s, %s, %s, %s, %s, to_timestamp(%s))
ON CONFLICT (city, measured_at) DO NOTHING;
"""

AQ_SQL = """
INSERT INTO staging.air_quality (city, station, pm25, pm10, source, measured_at)
VALUES (%s, %s, %s, %s, %s, %s)
ON CONFLICT (city, measured_at) DO NOTHING;
"""


def load_records(weather_records: list, aq_records: list) -> None:
    """Insert idempotent: chay lai nhieu lan khong tao duplicate."""
    run_ts = datetime.now(timezone.utc)
    with get_conn() as conn, conn.cursor() as cur:
        for w in weather_records:
            cur.execute(WEATHER_SQL, (
                w.city, w.temp_c, w.humidity,
                w.wind_speed_ms, w.weather, w.measured_at,
            ))
        for aq in aq_records:
            cur.execute(AQ_SQL, (
                aq.city, aq.station, aq.pm25, aq.pm10, aq.source, run_ts,
            ))
    logger.info("Loaded %d weather + %d air quality records",
                len(weather_records), len(aq_records))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
    from etl.extract import CITIES, extract_air_quality, extract_weather
    from etl.validate import validate_air_quality, validate_weather

    weather = [v for c in CITIES if (v := validate_weather(extract_weather(c)))]
    aq = [v for c in CITIES if (v := validate_air_quality(extract_air_quality(c)))]
    load_records(weather, aq)
