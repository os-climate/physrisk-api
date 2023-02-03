import json
import os

from flask import Blueprint, abort, current_app, request
from flask.helpers import make_response

import physrisk.requests
from physrisk.requests import get

api = Blueprint("api", __name__, url_prefix="/api")

@api.post("/get_hazard_data")
@api.post("/get_hazard_data_availability")
@api.post("/get_asset_impact")
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
    if not (resp_data.get("items") or resp_data.get("models") or resp_data.get("asset_impacts")):
        log.error(f"No results returned for '{request_id}' request")
        abort(404)

    return resp_data


@api.get('/images/<path:array_path>.png')
def get_image(array_path):
    """Request that physrisk converts an array to image.
    This is intended for small arrays, say <~ 1500x1500 pixels. Otherwise we use Mapbox to host
    tilesets (could consider storing tiles directly in S3 in future).  
    """
    log = current_app.logger
    log.info(f"Creating raster image for {array_path}.")
    min_value = request.args.get('minValue')
    min_value = float(min_value) if min_value is not None else None
    max_value = request.args.get('maxValue')
    max_value = float(max_value) if max_value is not None else None
    colormap = request.args.get('colormap') 

    image_binary = physrisk.requests.get_image(array_path, colormap="heating", max_value=max_value, min_value=min_value)
    response = make_response(image_binary)
    response.headers.set('Content-Type', 'image/png')

    return response

