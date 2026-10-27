
from pathlib import Path
import json
import logging

import requests


API_URL = "https://archive-api.open-meteo.com/v1/archive"

CITIES = {
    "Warsaw": {"latitude": 52.2297, "longitude": 21.0122},
    "Krakow": {"latitude": 50.0647, "longitude": 19.9450},
    "Gdansk": {"latitude": 54.3520, "longitude": 18.6466},
}

START_DATE = "2025-10-01"
END_DATE = "2025-10-07"

HOURLY_FIELDS = [
    "temperature_2m",
    "precipitation",
    "wind_speed_10m",
]

RAW_DATA_DIR = Path("data/raw")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


def fetch_weather(city: str, coordinates: dict) -> dict:
    """Fetch and validate hourly weather data for one city."""
    params = {
        "latitude": coordinates["latitude"],
        "longitude": coordinates["longitude"],
        "start_date": START_DATE,
        "end_date": END_DATE,
        "hourly": HOURLY_FIELDS,
        "timezone": "Europe/Warsaw",
    }

    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()

    if not isinstance(data, dict):
        raise ValueError(f"API response for {city} is not a JSON object")

    hourly = data.get("hourly")

    if not isinstance(hourly, dict):
        raise ValueError(f"Missing hourly data for {city}")

    times = hourly.get("time")

    if not isinstance(times, list) or not times:
        raise ValueError(f"Missing or empty hourly timestamps for {city}")

    for field in HOURLY_FIELDS:
        values = hourly.get(field)

        if not isinstance(values, list):
            raise ValueError(f"Missing or invalid field '{field}' for {city}")

        if len(values) != len(times):
            raise ValueError(
                f"Length mismatch for {city}, field '{field}': "
                f"{len(values)} values vs {len(times)} timestamps"
            )

    return {
        "city": city,
        "latitude": coordinates["latitude"],
        "longitude": coordinates["longitude"],
        "source": API_URL,
        "fetched_for_start_date": START_DATE,
        "fetched_for_end_date": END_DATE,
        "hourly": hourly,
    }


def main() -> int:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    failures = []

    for city, coordinates in CITIES.items():
        output_file = RAW_DATA_DIR / f"{city.lower()}_weather.json"
        temp_file = output_file.with_suffix(".json.tmp")

        logger.info("Fetching weather data for %s", city)

        try:
            data = fetch_weather(city, coordinates)

            with temp_file.open("w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)

            # Replace the previous file only after a successful write.
            temp_file.replace(output_file)

            logger.info(
                "Saved %d hourly records to %s",
                len(data["hourly"]["time"]),
                output_file,
            )

        except (requests.RequestException, ValueError, OSError) as error:
            failures.append(city)
            logger.exception("Failed to process %s: %s", city, error)

            if temp_file.exists():
                temp_file.unlink()

    if failures:
        logger.error("Extraction failed for: %s", ", ".join(failures))
        return 1

    logger.info("Extraction completed successfully for all cities")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
