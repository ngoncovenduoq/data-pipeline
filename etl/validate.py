"""Validate: kiem tra du lieu bang Pydantic truoc khi load vao Postgres."""
import logging
from typing import Optional

from pydantic import BaseModel, Field, ValidationError

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


class WeatherRecord(BaseModel):
    """Schema cho 1 ban ghi thoi tiet."""
    city: str
    temp_c: float = Field(ge=-60, le=60)        # nhiet do hop ly
    humidity: int = Field(ge=0, le=100)          # do am 0-100%
    wind_speed_ms: float = Field(ge=0)
    weather: str
    measured_at: int = Field(gt=0)               # unix timestamp


class AirQualityRecord(BaseModel):
    """Schema cho 1 ban ghi chat luong khong khi."""
    city: str
    station: str
    pm25: float = Field(ge=0)                    # bat buoc co, khong am
    pm10: Optional[float] = Field(default=None, ge=0)  # cho phep thieu
    source: str


def validate_weather(raw: dict) -> Optional[WeatherRecord]:
    """Tra ve record hop le, hoac None neu du lieu loi (co log)."""
    try:
        return WeatherRecord(**raw)
    except ValidationError as e:
        logger.error("Weather data invalid for %s: %s", raw.get("city"), e)
        return None


def validate_air_quality(raw: dict) -> Optional[AirQualityRecord]:
    try:
        return AirQualityRecord(**raw)
    except ValidationError as e:
        logger.error("Air quality data invalid for %s: %s", raw.get("city"), e)
        return None


if __name__ == "__main__":
    from etl.extract import CITIES, extract_air_quality, extract_weather

    for city in CITIES:
        w = validate_weather(extract_weather(city))
        aq = validate_air_quality(extract_air_quality(city))
        status_w = "OK" if w else "FAILED"
        status_aq = "OK" if aq else "FAILED"
        logger.info("%s | weather: %s | air quality: %s", city["name"], status_w, status_aq)
