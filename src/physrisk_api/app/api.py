import json
import os
from datetime import datetime, timedelta, timezone

import physrisk.requests
from flask import Blueprint, abort, current_app, jsonify, request
from flask.helpers import make_response
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, unset_jwt_cookies, verify_jwt_in_request
from physrisk.requests import get

api = Blueprint("api", __name__, url_prefix="/api")


@api.post("/token")
def create_token():
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    if email != "test" or password != os.environ["OSC_TEST_USER_KEY"]:
        return {"msg": "Wrong email or password"}, 401

    access_token = create_access_token(identity=email, additional_claims={"data_access": "osc"})
    response = {"access_token": access_token}
    return response


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
        try:
            verify_jwt_in_request(optional=True)
            # if no JWT, default to 'public' access level
            data_access = get_jwt()["data_access"]
        except Exception as exc_info:
            log.warning(f"No JWT for '{request_id}' request", exc_info=exc_info)
            data_access = "public"
        request_dict["group_ids"] = [data_access]
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


@api.get("/images/<path:resource>.png")
def get_image(resource):
    """Request that physrisk converts an array to image.
    This is intended for small arrays, say <~ 1500x1500 pixels. Otherwise we use Mapbox to host
    tilesets (could consider storing tiles directly in S3 in future).
    """
    log = current_app.logger
    log.info(f"Creating raster image for {resource}.")
    min_value = request.args.get("minValue")
    min_value = float(min_value) if min_value is not None else None
    max_value = request.args.get("maxValue")
    max_value = float(max_value) if max_value is not None else None
    colormap = request.args.get("colormap")
    scenarioId = request.args.get("scenarioId")
    year = int(request.args.get("year"))
    verify_jwt_in_request(optional=True)
    data_access = get_jwt().get("data_access", "public")
    image_binary = physrisk.requests.get_image(
        request_dict={
            "resource": resource,
            "colormap": "heating" if colormap is None else colormap,
            "scenarioId": scenarioId,
            "year": year,
            "group_ids": [data_access],
            "max_value": max_value,
            "min_value": min_value,
        }
    )
    response = make_response(image_binary)
    response.headers.set("Content-Type", "image/png")
    return response


@api.after_request
def refresh_expiring_jwts(response):
    try:
        verify_jwt_in_request(optional=True)
        jwt = get_jwt()
        if "exp" not in jwt:
            return response
        exp_timestamp = jwt["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            data = response.get_json()
            if type(data) is dict:
                data["access_token"] = access_token
                response.data = json.dumps(data)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original response
        return response


@api.post("/logout")
def logout():
    response = jsonify({"msg": "logout successful"})
    unset_jwt_cookies(response)
    return response


@api.post("/profile")
def profile():
    verify_jwt_in_request()
    identity = get_jwt_identity()
    response_body = {"id": identity}
    return response_body
