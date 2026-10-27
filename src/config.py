"""Central configuration for the weather data pipeline."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

API_URL = "https://archive-api.open-meteo.com/v1/archive"

CITIES = {
    "Warsaw": {"latitude": 52.2297, "longitude": 21.0122},
    "Krakow": {"latitude": 50.0647, "longitude": 19.9450},
    "Gdansk": {"latitude": 54.3520, "longitude": 18.6466},
}

START_DATE = "2025-10-01"
END_DATE = "2025-10-07"
TIMEZONE = "Europe/Warsaw"

HOURLY_FIELDS = [
    "temperature_2m",
    "precipitation",
    "wind_speed_10m",
]

RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DATA_DIR = PROJECT_ROOT / "data" / "processed"
