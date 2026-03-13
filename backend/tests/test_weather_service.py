from unittest.mock import MagicMock, patch

from requests import RequestException

from app.services.weather_service import (
    build_mock_weather_data,
    convert_to_celsius,
    fetch_weather_data,
)


MOCK_POINTS_RESPONSE = {
    "properties": {
        "forecast": "https://api.weather.gov/gridpoints/SEW/124,67/forecast"
    }
}

MOCK_FORECAST_RESPONSE = {
    "properties": {
        "periods": [
            {
                "temperature": 72,
                "shortForecast": "Partly Cloudy",
                "detailedForecast": "Partly cloudy with a high near 72.",
            }
        ]
    }
}


@patch("app.services.weather_service.requests.get")
def test_fetch_weather_data_returns_normalized_payload_on_success(mock_get):
    points_response = MagicMock()
    points_response.json.return_value = MOCK_POINTS_RESPONSE
    points_response.raise_for_status = MagicMock()

    forecast_response = MagicMock()
    forecast_response.json.return_value = MOCK_FORECAST_RESPONSE
    forecast_response.raise_for_status = MagicMock()

    mock_get.side_effect = [points_response, forecast_response]

    result = fetch_weather_data("Seattle")

    assert result["name"] == "Seattle"
    assert result["main"]["temp_f"] == 72
    assert result["main"]["temp_c"] == convert_to_celsius(72)
    assert result["main"]["temp"] == result["main"]["temp_c"]
    assert result["weather"][0]["main"] == "Partly Cloudy"


@patch("app.services.weather_service.requests.get")
@patch("app.services.weather_service.build_mock_weather_data")
def test_fetch_weather_data_falls_back_to_mock_on_request_failure(
    mock_build_mock_weather_data, mock_get
):
    fallback_payload = build_mock_weather_data()
    mock_build_mock_weather_data.return_value = fallback_payload
    mock_get.side_effect = RequestException("Connection error")

    result = fetch_weather_data("Seattle")

    assert result == fallback_payload
    mock_build_mock_weather_data.assert_called_once()
