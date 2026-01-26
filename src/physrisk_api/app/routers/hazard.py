"""Hazard-related endpoints for querying hazard data and availability."""

import logging
import logging.config
from physrisk_api.app.logging_config import LOGGING_CONFIG
from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException
from physrisk.requests import Requester
from physrisk.api.v1.hazard_data import (
    HazardAvailabilityRequest,
    HazardAvailabilityResponse,
    HazardDataRequest,
    HazardDataResponse,
)
from physrisk_api.app.routers.container import requester

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["hazard"])


@router.post("/get_hazard_data")
def get_hazard_data(
    request: HazardDataRequest, requester: Annotated[Requester, Depends(requester)]
) -> HazardDataResponse:
    """Obtain a list of hazard data. This request is made through the `get_hazard_data` function from `physrisk-lib`.

    Args:
        request (HazardDataRequest): Object containing the request parameters. This includes the list of hazard data requests. For each request, there is a pair of geographic coordinates, as well as the hazard type, indicator, year, and projection scenario. It also includes the desired interpolation.
        requester (Requester): Object that manages requests to the `physrisk-lib` services.

    Returns:
        HazardDataResponse: Object containing the list of hazard data. For each request, an object with the requested data is returned.

    Raises:
        HTTPException: If the request is invalid or if no results are returned.

    """
    try:
        response = requester.get_hazard_data(request)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=400, detail="Invalid 'get_hazard_data' request"
        ) from e
    if len(response.items) == 0:
        detail = "No results returned for 'get_hazard_data' request"
        logger.error(detail)
        raise HTTPException(status_code=404, detail=detail)
    return response


@router.post("/get_hazard_data_availability")
def get_hazard_data_availability(
    request: HazardAvailabilityRequest,
    requester: Annotated[Requester, Depends(requester)],
) -> HazardAvailabilityResponse:
    """Obtain the information for all the hazard resources.

    This information includes the next metadata:
        - Display name (used in the frontend).
        - Route for the maps and data inside the bucket of S3.
        - Scale, units, etc.
    In fact, this information is a version of the `inventory.json` adapted to the needs of the frontend.

    The function from `physrisk-lib` used to obtain this information is `get_hazard_data_availability`.

    Args:
        request (HazardAvailabilityRequest): At this moment, this object is not processed by the flow of `get_hazard_data_availability`. The idea could be limit the information to certain hazard types, indicators, etc. But at this moment, it is not implemented.
        requester (Requester): Object that manages requests to the `physrisk-lib` services.

    Returns:
        HazardAvailabilityResponse: Object containing the information about the hazard resources. This information is used to build the Hazard viewer in the frontend. As it was mentioned before, this information is the same from the `inventory.json`.

    """
    response = requester.get_hazard_data_availability(request)
    return response
