"""Source-related endpoints (arrays, rasters, and image generation)."""

import logging
import logging.config
from physrisk_api.app.logging_config import LOGGING_CONFIG
from typing import Annotated, Optional, Any
from fastapi import APIRouter, Depends, Path, Query, Response, HTTPException
from physrisk.requests import Requester
from physrisk.api.v1.hazard_image import (
    HazardImageRequest,
    Tile,
    # TileNotAvailableError,
    # HazardImageInfoRequest,
    # HazardImageInfoResponse,
)

from physrisk_api.app.routers.container import requester

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["sources"])


@router.get("/images/{resource:path}.{format}")
def get_image(
    resource: str,
    format: Annotated[str, Path(description="Image format", examples=["PNG"])],
    scenarioId: str,  # noqa: N803
    year: int,
    requester: Annotated[Requester, Depends(requester)],
    minValue: Annotated[  # noqa: N803
        Optional[float], Query(description="Minimum value", examples=[0])
    ] = None,
    maxValue: Annotated[  # noqa: N803
        Optional[float], Query(description="Maximum value", examples=[3])
    ] = None,
    colormap: Annotated[
        Optional[str], Query(description="Maximum value", examples=["flare"])
    ] = None,
):
    """Request that physrisk converts an array to image.

    A whole-aray image is created. This is  intended for small arrays, say <~ 1500x1500 pixels.
    Otherwise use tiled form of request.
    """
    logger.info(f"Creating whole-array image for {resource}.")
    image_binary = requester.get_image(
        HazardImageRequest(
            resource=resource,
            tile=None,
            colormap=colormap,
            format=format,
            scenario_id=scenarioId,
            year=year,
            group_ids=["osc"],
            max_value=maxValue,
            min_value=minValue,
        )
    )
    return Response(content=image_binary, media_type="image/png")


# @router.post("/get_image_info")
# def get_image_info(
#     request: HazardImageInfoRequest, requester: Annotated[Requester, Depends(requester)]
# ) -> HazardImageInfoResponse:
#     try:
#         response = requester.get_image_info(request)
#     except Exception as e:
#         logger.exception(e)
#         raise HTTPException(status_code=400, detail="Invalid 'get_image_info' request")
#     return response


@router.get("/tiles/{resource:path}/{z}/{x}/{y}.{format}")
def get_tile(
    resource: str,
    format: Annotated[str, Path(description="Image format", examples=["PNG"])],
    x: int,
    y: int,
    z: int,
    requester: Annotated[Requester, Depends(requester)],
    scenarioId: str,  # noqa: N803
    year: int,
    minValue: Annotated[  # noqa: N803
        Optional[float], Query(description="Minimum value", examples=[0])
    ] = None,
    maxValue: Annotated[  # noqa: N803
        Optional[float], Query(description="Maximum value", examples=[3])
    ] = None,
    colormap: Annotated[
        Optional[str], Query(description="Maximum value", examples=["flare"])
    ] = None,
    indexValue: Annotated[  # noqa: N803
        Optional[Any],
        Query(description="Index (non-spatial dimension) value", examples=[0]),
    ] = None,
):
    """Request that physrisk converts an array to image.

    The request will return the requested tile if an array pyramid exists; otherwise an
    exception is thrown.
    """
    logger.info(f"Creating raster image for {resource}.")
    try:
        image_binary = requester.get_image(
            HazardImageRequest(
                resource=resource,
                tile=Tile(x, y, z),
                colormap=colormap,
                format=format,
                scenario_id=scenarioId,
                year=year,
                group_ids=["osc"],
                max_value=maxValue,
                min_value=minValue,
                index_value=indexValue,
            )
        )
        return Response(content=image_binary, media_type="image/png")
    # except TileNotAvailableError as e:
    #     logger.error(f"No tile for array {e}")
    #     raise HTTPException(404)
    except Exception as e:
        logger.error(f"No tile: {e}")
        raise HTTPException(404) from e
