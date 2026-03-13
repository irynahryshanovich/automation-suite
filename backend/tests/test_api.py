from unittest.mock import patch


def test_get_state_returns_default_targets(test_client):
    response = test_client.get("/api/state")

    assert response.status_code == 200
    targets = {item["target"] for item in response.json()}
    assert targets == {"Twitter", "Facebook", "Instagram"}


def test_get_settings_returns_success(test_client):
    response = test_client.get("/api/settings")

    assert response.status_code == 200
    assert "app_name" in response.json()


def test_update_state_updates_valid_target(test_client):
    response = test_client.put("/api/state/Twitter", json={"status": "paused"})

    assert response.status_code == 200
    assert response.json() == {"target": "Twitter", "status": "paused"}


def test_update_state_returns_422_for_invalid_target(test_client):
    response = test_client.put("/api/state/UnknownTarget", json={"status": "paused"})

    assert response.status_code == 422


@patch("app.routes.api.perform_automation")
def test_run_automation_forwards_city_and_returns_service_response(mock_perform, test_client):
    mock_response = {
        "timestamp": "2025-03-10T12:00:00",
        "weather": {"main": {"temp": 22.0, "temp_c": 22.0, "temp_f": 71.6}},
        "sports": {"events": []},
        "actions": ["Activated Twitter ads"],
        "states": [],
    }
    mock_perform.return_value = mock_response

    response = test_client.post("/api/run", json={"city": "Seattle"})

    assert response.status_code == 200
    assert response.json() == mock_response
    mock_perform.assert_called_once_with("Seattle", source="manual")


def test_delete_logs_returns_success(test_client):
    response = test_client.delete("/api/logs")

    assert response.status_code == 200
