from unittest import mock
from fastapi.testclient import TestClient
from physrisk.api.v1.hazard_data import (
    # HazardAvailabilityRequest,
    # HazardDataRequest,
    ##HazardAvailabilityResponse,
    HazardDataResponse,
)
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
                        "return_periods": [
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


# def test_hazard_data_invalid_request(caplog):
#     app = create_app()
#     requester_mock = mock.Mock(spec=Requester)
#     with app.container.requester.override(requester_mock):
#         requester_mock.get.side_effect = ValueError()

#         with app.test_client() as test_client:
#             resp = do_hazard_data_request(test_client)

#         assert resp.status_code == 400
#         assert "Invalid 'get_hazard_data' request" in caplog.text


# def test_hazard_data_no_items_in_response(caplog):
#     app = create_app()
#     requester_mock = mock.Mock(spec=Requester)
#     with app.container.requester.override(requester_mock):
#         requester_mock.get.return_value = '{"items": []}'

#         with app.test_client() as test_client:
#             resp = do_hazard_data_request(test_client)

#         assert resp.status_code == 404
#         assert "No results returned for 'get_hazard_data' request" in caplog.text


# def test_hazard_inventory_typical():
#     app = create_app()
#     requester_mock = mock.Mock(spec=Requester)
#     with app.container.requester.override(requester_mock):
#         expected = {
#             "models": [
#                 {
#                     "event_type": "RiverineInundation",
#                     "id": "riverine_inundation/wri/v2/000000000WATCH",
#                     "scenarios": [{"id": "historical", "years": [1980]}],
#                 },
#                 {
#                     "event_type": "RiverineInundation",
#                     "id": "riverine_inundation/wri/v2/00000NorESM1-M",
#                     "scenarios": [
#                         {"id": "rcp4p5", "years": [2030, 2050, 2080]},
#                         {"id": "rcp8p5", "years": [2030, 2050, 2080]},
#                     ],
#                 },
#                 {
#                     "event_type": "RiverineInundation",
#                     "id": "riverine_inundation/wri/v2/0000GFDL-ESM2M",
#                     "scenarios": [
#                         {"id": "rcp4p5", "years": [2030, 2050, 2080]},
#                         {"id": "rcp8p5", "years": [2030, 2050, 2080]},
#                     ],
#                 },
#             ]
#         }
#         # We don't need to test external libraries here, so mock physrisk's
#         # `get()` with realistic reponse to avoid looking up real data.
#         requester_mock.get.return_value = json.dumps(expected)

#         with app.test_client() as test_client:
#             resp = test_client.post("/api/get_hazard_data_availability", json={})

#         assert resp.status_code == 200
#         assert resp.json == expected


# def test_hazard_inventory_invalid_request(caplog):
#     app = create_app()
#     requester_mock = mock.Mock(spec=Requester)
#     with app.container.requester.override(requester_mock):
#         requester_mock.get.side_effect = ValueError()

#         with app.test_client() as test_client:
#             resp = test_client.post("/api/get_hazard_data_availability", json={})

#         assert resp.status_code == 400
#         assert "Invalid 'get_hazard_data_availability' request" in caplog.text


# def test_hazard_inventory_no_items_in_response(caplog):
#     app = create_app()
#     requester_mock = mock.Mock(spec=Requester)
#     with app.container.requester.override(requester_mock):
#         requester_mock.get.return_value = '{"models": []}'

#         with app.test_client() as test_client:
#             resp = test_client.post("/api/get_hazard_data_availability", json={})

#         assert resp.status_code == 404
#         assert (
#             "No results returned for 'get_hazard_data_availability' request"
#             in caplog.text
#         )
