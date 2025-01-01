from unittest import mock
from fastapi.testclient import TestClient
from physrisk.api.v1.hazard_data import (
    # HazardAvailabilityRequest,
    # HazardDataRequest,
    HazardAvailabilityResponse,
    HazardDataResponse,
)
from physrisk.data.inventory import EmbeddedInventory
from physrisk.requests import Requester

from physrisk_api.app.main import app

client = TestClient(app)


def test_hello_world():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Physrisk API"}


# For mocking, we could do something like this using FastAPI's functionality to override
# a dependency or we can use unittest.mock (which we do):
# requester_mock = mock.Mock(spec=Requester)
# async def override_requester():
#     return requester_mock
# app.dependency_overrides[requester] = override_requester
# requester_mock.get_hazard_data.return_value = response


def hazard_data_request():
    """A minimal get_hazard_data request for testing purposes."""

    return {
        "items": [
            {
                "request_item_id": "afac2a5d-9961-...",
                "hazard_type": "RiverineInundation",
                "indicator_id": "flood_depth",
                "longitudes": [20.24506],
                "latitudes": [45.48358],
                "year": 1985,
                "scenario": "historical",
                "path": "inundation/river_tudelft/v2/flood_depth_unprot_{scenario}_{year}",
            }
        ],
    }


def test_get_hazard_data_typical():
    expected = {
        "items": [
            {
                "event_type": "RiverineInundation",
                "intensity_curve_set": [
                    {
                        "intensities": [0.0, 0.1, 0.2, 1.0, 1.0, 1.0, 1.0, 1.0],
                        "index_values": [
                            5.0,
                            10.0,
                            25.0,
                            50.0,
                            100.0,
                            250.0,
                            500.0,
                            1000.0,
                        ],
                    }
                ],
                "model": "...",
                "request_item_id": "afac2a5d-9961-...",
                "scenario": "historical",
                "year": 1985,
            }
        ],
    }
    response = HazardDataResponse(**expected)
    # we do not need to test external libraries here, so mock physrisk
    # with realistic response to avoid looking up real data.
    with mock.patch.object(Requester, "get_hazard_data", return_value=response):
        resp = client.post("/api/get_hazard_data", json=hazard_data_request())

    assert resp.status_code == 200
    assert (
        resp.json()["items"][0]["intensity_curve_set"][0]["intensities"]
        == expected["items"][0]["intensity_curve_set"][0]["intensities"]
    )


def test_hazard_data_invalid_request(caplog):
    with mock.patch.object(Requester, "get_hazard_data", side_effect=ValueError()):
        resp = client.post("/api/get_hazard_data", json=hazard_data_request())

    assert resp.status_code == 400
    assert "ValueError" in caplog.text


def test_hazard_data_no_items_in_response(caplog):
    with mock.patch.object(
        Requester, "get_hazard_data", return_value=HazardDataResponse(items=[])
    ):
        resp = client.post("/api/get_hazard_data", json=hazard_data_request())

    assert resp.status_code == 404
    assert "No results returned for 'get_hazard_data' request" in caplog.text


def test_hazard_data_availability_typical():
    inventory = EmbeddedInventory()
    expected = HazardAvailabilityResponse(
        models=[list(inventory.resources.values())[0]], colormaps={}
    )
    with mock.patch.object(
        Requester, "get_hazard_data_availability", return_value=expected
    ):
        resp = client.post("/api/get_hazard_data_availability", json={})

        assert resp.status_code == 200
        assert resp.json()["models"][0]["path"] == expected.models[0].path
