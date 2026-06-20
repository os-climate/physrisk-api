"""Asset-related endpoints for computing exposure and impact."""

import logging
import logging.config
from physrisk_api.app.logging_config import LOGGING_CONFIG
from typing import Annotated
from fastapi import Depends, APIRouter, HTTPException
from physrisk.requests import Requester
from physrisk.api.v1.exposure_req_resp import (
    AssetExposureRequest,
    AssetExposureResponse,
)
from physrisk.api.v1.impact_req_resp import AssetImpactRequest, AssetImpactResponse
from physrisk_api.app.auth import get_current_user, provider_limits
from physrisk_api.app.routers.container import requester

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["asset"])


@router.post("/get_asset_exposure")
def get_asset_exposure(
    request: AssetExposureRequest,
    requester: Annotated[Requester, Depends(requester)],
    user: Annotated[dict, Depends(get_current_user)],
) -> AssetExposureResponse:
    """Retrieve the hazard exposure for a portfolio of assets.

    Args:
        request (AssetExposureRequest): Contains asset
            details and parameters required to compute hazard exposures.
        requester (Requester): Object that manages requests to the `physrisk` calculation engine.

    Returns:
        AssetExposureResponse: Contains asset exposure information.

    """
    request.provider_max_requests = provider_limits(user)
    response = requester.get_asset_exposures(request)
    return response


@router.post("/get_asset_impact")
def get_asset_impact(
    request: AssetImpactRequest,
    requester: Annotated[Requester, Depends(requester)],
    user: Annotated[dict, Depends(get_current_user)],
) -> AssetImpactResponse:
    """Calculate asset impact results for a portfolio of assets, for a given set of projection years, and scenarios.
    Results comprise quantitative asset-level impacts and scores inferred from these.

    Args:
        request (AssetImpactRequest): The request body containing asset portfolio with their details, along with the
            scenarios, years, and settings (including scope of hazards to be evaluated).
        requester (Requester): Object that manages requests to the `physrisk` calculation engine.

    Returns:
        AssetImpactResponse : The calculated impacts and scores for the requested assets, according to request settings.

    Raises:
        HTTPException:
            - 400: If the request is invalid or an error occurs while computing asset impacts.

    """
    request.provider_max_requests = provider_limits(user)
    try:
        response = requester.get_asset_impacts(request)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=400, detail="Invalid 'get_asset_impact' request"
        ) from e
    return response


@router.get("/get_example_portfolios")
def get_example_portfolios(requester: Annotated[Requester, Depends(requester)]):
    try:
        response = requester.get_example_portfolios()
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=400, detail="Error getting example portfolios")
    return response
