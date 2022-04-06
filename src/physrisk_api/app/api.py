import json
import os

from flask import Blueprint, abort, current_app, request
from physrisk.requests import get

api = Blueprint("api", __name__, url_prefix="/api")


@api.get("/get_hazard_data")
@api.get("/get_hazard_data_availability")
def hazard_data():
    """Retrieve data from physrisk library based on request URL and JSON data."""

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

    # Response object should hold a list of items or models.
    # If not, none were found matching the request's criteria.
    if not (resp_data.get("items") or resp_data.get("models")):
        log.error(f"No results returned for '{request_id}' request")
        abort(404)

    return resp_data
