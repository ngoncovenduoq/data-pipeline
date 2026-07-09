"""Test cho tang validate: du lieu tot phai pass, du lieu ban phai bi chan."""
from etl.validate import validate_air_quality, validate_weather

GOOD_WEATHER = {
    "city": "Hanoi",
    "temp_c": 29.5,
    "humidity": 78,
    "wind_speed_ms": 2.9,
    "weather": "Rain",
    "measured_at": 1751970000,
}

GOOD_AQ = {
    "city": "Hanoi",
    "station": "US Diplomatic Post: Hanoi",
    "pm25": 12.9,
    "pm10": None,
    "source": "openaq",
}


def test_valid_weather_passes():
    record = validate_weather(GOOD_WEATHER)
    assert record is not None
    assert record.city == "Hanoi"
    assert record.temp_c == 29.5


def test_valid_air_quality_passes():
    record = validate_air_quality(GOOD_AQ)
    assert record is not None
    assert record.pm10 is None  # pm10 duoc phep thieu


def test_impossible_temperature_rejected():
    bad = {**GOOD_WEATHER, "temp_c": 999}
    assert validate_weather(bad) is None


def test_negative_pm25_rejected():
    bad = {**GOOD_AQ, "pm25": -5}
    assert validate_air_quality(bad) is None


def test_humidity_over_100_rejected():
    bad = {**GOOD_WEATHER, "humidity": 150}
    assert validate_weather(bad) is None


def test_missing_field_rejected():
    bad = {k: v for k, v in GOOD_WEATHER.items() if k != "city"}
    assert validate_weather(bad) is None
