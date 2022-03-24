import json
import unittest.mock as mock

from physrisk_api.app import create_app


def do_hazard_data_request(client):
    """A minimal get_hazard_data request for testing purposes."""

    return client.get(
        "/api/get_hazard_data",
        json={
            "items": [
                {
                    "request_item_id": "afac2a5d-9961-...",
                    "event_type": "RiverineInundation",
                    "longitudes": [69.4787],
                    "latitudes": [35.9416],
                    "year": 2080,
                    "scenario": "rcp8p5",
                    "model": "MIROC-ESM-CHEM",
                }
            ],
        },
    )


@mock.patch("physrisk_api.app.api.get")
def test_hazard_data_typical(mock_get):
    app = create_app()

    expected = {
        "items": [
            {
                "event_type": "RiverineInundation",
                "intensity_curve_set": [
                    {
                        "intensities": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                        "return_periods": [5.0, 10.0, 25.0, 50.0, 100.0, 250.0, 500.0, 1000.0],
                    }
                ],
                "model": "MIROC-ESM-CHEM",
                "request_item_id": "afac2a5d-9961-...",
                "scenario": "rcp8p5",
                "year": 2080,
            }
        ],
    }
    # We don't need to test external libraries here, so mock physrisk's
    # `get()` with realistic reponse to avoid looking up real data.
    mock_get.return_value = json.dumps(expected)

    with app.test_client() as test_client:
        resp = do_hazard_data_request(test_client)

    assert resp.status_code == 200
    assert resp.json == expected


@mock.patch("physrisk_api.app.api.get")
def test_hazard_data_invalid_request(mock_get, caplog):
    app = create_app()

    mock_get.side_effect = ValueError()

    with app.test_client() as test_client:
        resp = do_hazard_data_request(test_client)

    assert resp.status_code == 400
    assert "Invalid 'get_hazard_data' request" in caplog.text


@mock.patch("physrisk_api.app.api.get")
def test_hazard_data_no_items_in_response(mock_get, caplog):
    app = create_app()

    mock_get.return_value = '{"items": []}'

    with app.test_client() as test_client:
        resp = do_hazard_data_request(test_client)

    assert resp.status_code == 404
    assert "No items found for 'get_hazard_data' request" in caplog.text
