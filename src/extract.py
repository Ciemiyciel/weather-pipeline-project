
from pathlib import Path
import json

import requests


API_URL = "https://archive-api.open-meteo.com/v1/archive"

CITIES = {
    "Warsaw": {"latitude": 52.2297, "longitude": 21.0122},
    "Krakow": {"latitude": 50.0647, "longitude": 19.9450},
    "Gdansk": {"latitude": 54.3520, "longitude": 18.6466},
}

START_DATE = "2025-10-01"
END_DATE = "2025-10-07"

RAW_DATA_DIR = Path("data/raw")


def fetch_weather(city: str, coordinates: dict) -> dict:
    """Fetch historical hourly weather data for one city."""
    params = {
        "latitude": coordinates["latitude"],
        "longitude": coordinates["longitude"],
        "start_date": START_DATE,
        "end_date": END_DATE,
        "hourly": [
            "temperature_2m",
            "precipitation",
            "wind_speed_10m",
        ],
        "timezone": "Europe/Warsaw",
    }

    response = requests.get(API_URL, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()

    if "hourly" not in data or "time" not in data["hourly"]:
        raise ValueError(f"Unexpected API response for {city}")

    return {
        "city": city,
        "latitude": coordinates["latitude"],
        "longitude": coordinates["longitude"],
        "source": API_URL,
        "fetched_for_start_date": START_DATE,
        "fetched_for_end_date": END_DATE,
        "hourly": data["hourly"],
    }


def main() -> None:
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    for city, coordinates in CITIES.items():
        print(f"Fetching weather data for {city}...")

        try:
            data = fetch_weather(city, coordinates)
            output_file = RAW_DATA_DIR / f"{city.lower()}_weather.json"

            with output_file.open("w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=2)

            print(
                f"Saved {len(data['hourly']['time'])} hourly records "
                f"to {output_file}"
            )

        except (requests.RequestException, ValueError) as error:
            print(f"Failed to fetch data for {city}: {error}")


if __name__ == "__main__":
    main()


