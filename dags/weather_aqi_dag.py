"""DAG: pipeline thoi tiet + chat luong khong khi, chay moi 30 phut."""
from datetime import datetime, timedelta

from airflow.decorators import dag, task


@dag(
    dag_id="weather_aqi_pipeline",
    schedule="*/30 * * * *",
    start_date=datetime(2026, 7, 1),
    catchup=False,
    default_args={"retries": 2, "retry_delay": timedelta(minutes=2)},
    tags=["weather", "air-quality"],
)
def weather_aqi_pipeline():

    @task
    def extract_and_validate() -> dict:
        from etl.extract import CITIES, extract_air_quality, extract_weather
        from etl.validate import validate_air_quality, validate_weather

        weather = [v for c in CITIES if (v := validate_weather(extract_weather(c)))]
        aq = [v for c in CITIES if (v := validate_air_quality(extract_air_quality(c)))]
        return {
            "weather": [w.model_dump() for w in weather],
            "aq": [a.model_dump() for a in aq],
        }

    @task
    def load_to_staging(data: dict) -> None:
        from etl.load import load_records
        from etl.validate import AirQualityRecord, WeatherRecord

        weather = [WeatherRecord(**w) for w in data["weather"]]
        aq = [AirQualityRecord(**a) for a in data["aq"]]
        load_records(weather, aq)

    @task
    def transform_to_dw() -> None:
        from etl.transform import transform
        transform()

    transform_to_dw() << load_to_staging(extract_and_validate())


weather_aqi_pipeline()
