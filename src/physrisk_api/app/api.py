import json
import os

from flask import Blueprint, abort, current_app, request
from physrisk.requests import get

api = Blueprint("api", __name__, url_prefix="/api")


@api.get("/get_hazard_data")
def hazard_data():
    """Retrieve data objects with intensity curves for the requested
    parameters.

    Expected request data example:
    {
        "items": [
            {
                "item_id": "afac2a5d-9961-4f7b-af70-e7b6f46df20e",
                "event_type": "RiverineInundation",
                "longitudes": [69.4787],
                "latitudes": [35.9416],
                "year": 2080,
                "scenario": "rcp8p5",
                "model": "MIROC-ESM-CHEM"
            },
            ...
        ]
    }
    """

    log = current_app.logger
    request_id = os.path.basename(request.path)
    request_dict = request.json

    log.debug(f"Received '{request_id}' request")

    try:
        resp_data = get(request_id=request_id, request_dict=request_dict)
        resp_data = json.loads(resp_data)
    except Exception as exc_info:
        log.error(f"Invalid '{request_id}' request", exc_info=exc_info)
        abort(400)

    # Response object should hold a list of items.
    # If not, no items were found matching the request's criteria.
    if not resp_data.get("items"):
        log.error(f"No items found for '{request_id}' request")
        abort(404)

    return resp_data
