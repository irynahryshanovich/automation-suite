from unittest.mock import MagicMock, patch

from requests import RequestException

from app.services.sports_service import (
    build_mock_sports_data,
    fetch_sports_data,
)

MOCK_API_RESPONSE = {
    "events": [
        {
            "strEvent": "Lakers vs Celtics",
            "intHomeScore": "110",
            "intAwayScore": "105",
            "dateEvent": "2025-03-10",
            "strStatus": "Finished",
            "strHomeTeam": "Lakers",
            "strAwayTeam": "Celtics",
        }
    ]
}


@patch("app.services.sports_service.settings")
@patch("app.services.sports_service.requests.get")
def test_fetch_sports_data_uses_mock_payload_for_demo_key(mock_get, mock_settings):
    mock_settings.SPORTS_API_KEY = "demo_key"

    result = fetch_sports_data()

    mock_get.assert_not_called()
    assert "events" in result
    assert len(result["events"]) > 0


@patch("app.services.sports_service.settings")
@patch("app.services.sports_service.requests.get")
def test_fetch_sports_data_returns_api_payload_when_request_succeeds(mock_get, mock_settings):
    mock_settings.SPORTS_API_KEY = "real_api_key"
    mock_response = MagicMock()
    mock_response.json.return_value = MOCK_API_RESPONSE
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    result = fetch_sports_data()

    assert result == MOCK_API_RESPONSE
    mock_get.assert_called_once()


@patch("app.services.sports_service.settings")
@patch("app.services.sports_service.requests.get")
@patch("app.services.sports_service.build_mock_sports_data")
def test_fetch_sports_data_falls_back_to_mock_on_request_failure(
    mock_build_mock_sports_data, mock_get, mock_settings
):
    mock_settings.SPORTS_API_KEY = "real_api_key"
    fallback_payload = build_mock_sports_data()
    mock_build_mock_sports_data.return_value = fallback_payload
    mock_get.side_effect = RequestException("API timeout")

    result = fetch_sports_data()

    assert result == fallback_payload
    mock_build_mock_sports_data.assert_called_once()
