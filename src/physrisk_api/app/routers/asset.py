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
from physrisk_api.app.routers.container import requester

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["asset"])


@router.post("/get_asset_exposure")
def get_asset_exposure(
    request: AssetExposureRequest, requester: Annotated[Requester, Depends(requester)]
) -> AssetExposureResponse:
    """Retrieve hazard exposure information for an asset.

    This endpoint uses the functionality provided by ``physrisk-lib``, specifically `get_asset_exposures`.

    Args:
        request (AssetExposureRequest): The request body containing the asset
            details and parameters required to compute hazard exposures.
        requester (Requester): Dependency that provides access to the service to
            use `physrisk-lib` to compute asset exposures.

    Returns:
        AssetExposureResponse: Response for asset exposure information.

    """
    response = requester.get_asset_exposures(request)
    return response


@router.post("/get_asset_impact")
def get_asset_impact(
    request: AssetImpactRequest, requester: Annotated[Requester, Depends(requester)]
) -> AssetImpactResponse:
    """Retrieve impact data for a group of assets, given a set of hazards (indicators), projection years, and scenarios.

    To do so, it directly uses the functionality provided by `physrisk-lib` called `get_asset_impacts`.

    Args:
        request (AssetImpactRequest): The request body containing asset portfolio with their details, along with the
            scenarios, years, and hazards to be evaluated.
        requester (Requester): Dependency that provides access to the service
            responsible for computing asset impacts.

    Returns:
        AssetImpactResponse : The calculated impact
        data for the specified assets and hazards. The return type are different deppending on the processing of the request. CustomAssetImpactResponse is created in this API and it is documented, while AssetImpactResponse is the original response from physrisk-lib, which is not documented in this repository

    Raises:
        HTTPException:
            - 400: If the request is invalid or an error occurs while computing asset impacts.

    """
    try:
        response = requester.get_asset_impacts(request)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=400, detail="Invalid 'get_asset_impact' request"
        ) from e
    return response
