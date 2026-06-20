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
    StaticInformationResponse,
)
from physrisk_api.app.auth import get_current_user, provider_limits
from physrisk_api.app.routers.container import requester

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["hazard"])


@router.post("/get_hazard_data")
def get_hazard_data(
    request: HazardDataRequest,
    requester: Annotated[Requester, Depends(requester)],
    user: Annotated[dict, Depends(get_current_user)],
) -> HazardDataResponse:
    """Obtain hazard data for a set of locations.

    Args:
        request (HazardDataRequest): Hazard data request items. Each item comprises location data, as well as the hazard type, indicator, year, and historical/projection scenario.
        requester (Requester): Object that manages requests to the `physrisk` calculation engine.

    Returns:
        HazardDataResponse: Object containing the list of hazard data. For each request, an object with the requested data is returned.

    Raises:
        HTTPException: If the request is invalid or if no results are returned.

    """

    request.provider_max_requests = provider_limits(user)
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


@router.get("/get_static_information")
def get_static_information(
    requester: Annotated[Requester, Depends(requester)],
) -> StaticInformationResponse:
    """Return static information: scenario descriptions and OED occupancy codes."""
    return requester.get_static_information()


@router.post("/get_hazard_data_availability")
def get_hazard_data_availability(
    request: HazardAvailabilityRequest,
    requester: Annotated[Requester, Depends(requester)],
) -> HazardAvailabilityResponse:
    """Obtain information about available hazard resources.

    This information largely encapsulates `inventory.json` adapted to the needs of the frontend.

    Args:
        request (HazardAvailabilityRequest): Currently unused, but reserved for future extensions.
        requester (Requester): Object that manages requests to the `physrisk` calculation engine.

    Returns:
        HazardAvailabilityResponse: Contains information about available hazard resources.

    """
    response = requester.get_hazard_data_availability(request)
    return response
