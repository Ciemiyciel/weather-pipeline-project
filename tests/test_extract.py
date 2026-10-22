
from unittest.mock import Mock

import pytest

from src.extract import fetch_weather


CITY = "Warsaw"
COORDINATES = {"latitude": 52.2297, "longitude": 21.0122}


def make_response(hourly):
    response = Mock()
    response.json.return_value = {"hourly": hourly}
    response.raise_for_status.return_value = None
    return response


def test_fetch_weather_success(monkeypatch):
    hourly = {
        "time": ["2025-10-01T00:00", "2025-10-01T01:00"],
        "temperature_2m": [10.0, 9.5],
        "precipitation": [0.0, 0.2],
        "wind_speed_10m": [12.0, 15.0],
    }

    response = make_response(hourly)
    mock_get = Mock(return_value=response)
    monkeypatch.setattr("src.extract.requests.get", mock_get)

    result = fetch_weather(CITY, COORDINATES)

    assert result["city"] == CITY
    assert len(result["hourly"]["time"]) == 2
    mock_get.assert_called_once()


def test_fetch_weather_rejects_missing_field(monkeypatch):
    hourly = {
        "time": ["2025-10-01T00:00"],
        "temperature_2m": [10.0],
        "precipitation": [0.0],
        # Missing wind_speed_10m
    }

    monkeypatch.setattr(
        "src.extract.requests.get",
        Mock(return_value=make_response(hourly)),
    )

    with pytest.raises(ValueError, match="wind_speed_10m"):
        fetch_weather(CITY, COORDINATES)


def test_fetch_weather_rejects_mismatched_lengths(monkeypatch):
    hourly = {
        "time": ["2025-10-01T00:00", "2025-10-01T01:00"],
        "temperature_2m": [10.0],
        "precipitation": [0.0, 0.2],
        "wind_speed_10m": [12.0, 15.0],
    }

    monkeypatch.setattr(
        "src.extract.requests.get",
        Mock(return_value=make_response(hourly)),
    )

    with pytest.raises(ValueError, match="Length mismatch"):
        fetch_weather(CITY, COORDINATES)
