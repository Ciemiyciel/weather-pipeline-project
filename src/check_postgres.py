
"""Validate weather data stored in PostgreSQL."""

import logging

from config import CITIES
from load_postgres import postgres_connection

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


def check_data_quality():
    """Run quality checks and fail if invalid data is found."""
    with postgres_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    COUNT(*),
                    COUNT(*) FILTER (
                        WHERE city IS NULL OR timestamp IS NULL
                    ),
                    COUNT(*) FILTER (
                        WHERE temperature_2m IS NOT NULL
                          AND (temperature_2m < -90
                               OR temperature_2m > 65)
                    ),
                    COUNT(*) FILTER (
                        WHERE precipitation IS NOT NULL
                          AND precipitation < 0
                    ),
                    COUNT(*) FILTER (
                        WHERE wind_speed_10m IS NOT NULL
                          AND wind_speed_10m < 0
                    )
                FROM weather_observations;
            """)

            total, missing_keys, bad_temp, bad_rain, bad_wind = (
                cursor.fetchone()
            )

            cursor.execute("""
                SELECT city, COUNT(*)
                FROM weather_observations
                GROUP BY city
                ORDER BY city;
            """)
            city_counts = dict(cursor.fetchall())

    logger.info("Total observations: %s", total)
    logger.info("Observations by city: %s", city_counts)

    errors = []

    if total == 0:
        errors.append("The table is empty.")

    if missing_keys:
        errors.append(f"{missing_keys} rows have missing city/timestamp.")

    if bad_temp:
        errors.append(f"{bad_temp} rows have implausible temperatures.")

    if bad_rain:
        errors.append(f"{bad_rain} rows have negative precipitation.")

    if bad_wind:
        errors.append(f"{bad_wind} rows have negative wind speed.")

    expected_cities = set(CITIES)
    actual_cities = set(city_counts)

    if actual_cities != expected_cities:
        errors.append(
            f"Unexpected cities. Expected {sorted(expected_cities)}, "
            f"found {sorted(actual_cities)}."
        )

    if errors:
        for error in errors:
            logger.error(error)
        raise RuntimeError("Data quality checks failed.")

    logger.info("All data quality checks passed.")


if __name__ == "__main__":
    check_data_quality()
