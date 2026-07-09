"""Extract: OpenWeather (thoi tiet) + OpenAQ (chat luong khong khi)."""
import os

import requests
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_KEY = os.getenv("OPENWEATHER_API_KEY")
OPENAQ_KEY = os.getenv("OPENAQ_API_KEY")

CITIES = [
    {"name": "Hanoi", "lat": 21.0285, "lon": 105.8542},
    {"name": "Ho Chi Minh City", "lat": 10.7769, "lon": 106.7009},
    {"name": "Da Nang", "lat": 16.0544, "lon": 108.2022},
    {"name": "Da Lat", "lat": 11.9404, "lon": 108.4583},
    {"name": "Singapore", "lat": 1.3521, "lon": 103.8198},
    {"name": "Tokyo", "lat": 35.6762, "lon": 139.6503},
    {"name": "Beijing", "lat": 39.9042, "lon": 116.4074},
]


def extract_weather(city: dict) -> dict:
    """Lay thoi tiet hien tai cua 1 thanh pho tu OpenWeather."""
    params = {
        "lat": city["lat"],
        "lon": city["lon"],
        "appid": OPENWEATHER_KEY,
        "units": "metric",  # tra ve do C
    }
    resp = requests.get(
        "https://api.openweathermap.org/data/2.5/weather",
        params=params, timeout=10,
    )
    resp.raise_for_status()
    d = resp.json()
    return {
        "city": city["name"],
        "temp_c": d["main"]["temp"],
        "humidity": d["main"]["humidity"],
        "wind_speed_ms": d["wind"]["speed"],
        "weather": d["weather"][0]["main"],
        "measured_at": d["dt"],  # unix timestamp
    }


def extract_air_quality(city: dict) -> dict:
    """Thu toi da 10 tram OpenAQ gan nhat, tram nao co PM2.5 thi lay.
    Neu khong tram nao co du lieu -> fallback sang OpenWeather."""
    headers = {"X-API-Key": OPENAQ_KEY}

    loc_resp = requests.get(
        "https://api.openaq.org/v3/locations",
        params={
            "coordinates": f"{city['lat']},{city['lon']}",
            "radius": 25000,
            "limit": 10,
        },
        headers=headers, timeout=10,
    )
    loc_resp.raise_for_status()

    for loc in loc_resp.json()["results"]:
        sensor_map = {s["id"]: s["parameter"]["name"] for s in loc["sensors"]}
        latest_resp = requests.get(
            f"https://api.openaq.org/v3/locations/{loc['id']}/latest",
            headers=headers, timeout=10,
        )
        latest_resp.raise_for_status()
        values = {
            sensor_map.get(r["sensorsId"]): r["value"]
            for r in latest_resp.json()["results"]
        }
        if values.get("pm25") is not None:
            return {
                "city": city["name"],
                "station": loc["name"],
                "pm25": values.get("pm25"),
                "pm10": values.get("pm10"),
                "source": "openaq",
            }

    # Khong tram nao co du lieu -> dung OpenWeather Air Pollution
    return extract_air_quality_openweather(city)


def extract_air_quality_openweather(city: dict) -> dict:
    """Fallback: lay PM2.5/PM10 tu OpenWeather Air Pollution API."""
    resp = requests.get(
        "https://api.openweathermap.org/data/2.5/air_pollution",
        params={"lat": city["lat"], "lon": city["lon"], "appid": OPENWEATHER_KEY},
        timeout=10,
    )
    resp.raise_for_status()
    comp = resp.json()["list"][0]["components"]
    return {
        "city": city["name"],
        "station": "OpenWeather (satellite model)",
        "pm25": comp["pm2_5"],
        "pm10": comp["pm10"],
        "source": "openweather",
    }


if __name__ == "__main__":
    for city in CITIES:
        w = extract_weather(city)
        aq = extract_air_quality(city)
        print(f"--- {city['name']} ---")
        print(f"  Thoi tiet: {w['weather']} | {w['temp_c']}°C | "
              f"Do am {w['humidity']}% | Gio {w['wind_speed_ms']} m/s")
        print(f"  Tram: {aq['station']} ({aq['source']}) | "
              f"PM2.5: {aq['pm25']} | PM10: {aq['pm10']}")
