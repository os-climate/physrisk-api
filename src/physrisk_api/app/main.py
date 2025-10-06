import logging
import logging.config
from typing import Annotated, Any, Optional
from fastapi import Depends, FastAPI, HTTPException, Path, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from physrisk.api.v1.exposure_req_resp import (
    AssetExposureRequest,
    AssetExposureResponse,
)
from physrisk.api.v1.hazard_data import (
    HazardAvailabilityRequest,
    HazardAvailabilityResponse,
    HazardDataRequest,
    HazardDataResponse,
)
from physrisk.api.v1.hazard_image import (
    HazardImageRequest,
    Tile,
    TileNotAvailableError,
    HazardImageInfoRequest,
    HazardImageInfoResponse,
)
from physrisk.api.v1.impact_req_resp import AssetImpactRequest, AssetImpactResponse
from physrisk.requests import Requester
import uvicorn

from physrisk_api.app.container import create_container
from physrisk_api.app.logging_config import LOGGING_CONFIG


logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
container = create_container()
app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def requester():
    # We mainly use FastAPI's own dependency injection via Depends, but dependencies can have access to
    #  dependency_injector's declarative container.
    return container.requester()


@app.get("/")
async def root():
    logger.info("Physrisk API")
    return {"message": "Physrisk API"}


@app.post("/api/get_hazard_data")
def get_hazard_data(
    request: HazardDataRequest, requester: Annotated[Requester, Depends(requester)]
) -> HazardDataResponse:
    try:
        response = requester.get_hazard_data(request)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=400, detail="Invalid 'get_hazard_data' request")
    if len(response.items) == 0:
        detail = "No results returned for 'get_hazard_data' request"
        logger.error(detail)
        raise HTTPException(status_code=404, detail=detail)
    return response


@app.post("/api/get_hazard_data_availability")
def get_hazard_data_availability(
    request: HazardAvailabilityRequest,
    requester: Annotated[Requester, Depends(requester)],
) -> HazardAvailabilityResponse:
    response = requester.get_hazard_data_availability(request)
    return response


@app.post("/api/get_asset_exposure")
def get_asset_exposure(
    request: AssetExposureRequest, requester: Annotated[Requester, Depends(requester)]
) -> AssetExposureResponse:
    response = requester.get_asset_exposures(request)
    return response


@app.post("/api/get_asset_impact")
def get_asset_impact(
    request: AssetImpactRequest, requester: Annotated[Requester, Depends(requester)]
) -> AssetImpactResponse:
    try:
        response = requester.get_asset_impacts(request)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=400, detail="Invalid 'get_asset_impact' request"
        )
    return response


@app.get("/api/images/{resource:path}.{format}")
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


@app.post("/api/get_image_info")
def get_image_info(
    request: HazardImageInfoRequest, requester: Annotated[Requester, Depends(requester)]
) -> HazardImageInfoResponse:
    try:
        response = requester.get_image_info(request)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(status_code=400, detail="Invalid 'get_image_info' request")
    return response


@app.get("/api/tiles/{resource:path}/{z}/{x}/{y}.{format}")
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
    except TileNotAvailableError as e:
        logger.error(f"No tile for array {e}")
        raise HTTPException(404)
    except Exception as e:
        logger.error(f"No tile: {e}")
        raise HTTPException(404)


@app.get("/api/reset")
def reset():
    container.reset_singletons()
    return "Reset successful"


if __name__ == "__main__":
    # this is so that one can debug via, e.g. Python Debugger: Current File on main.py
    uvicorn.run(app, host="0.0.0.0", port=8000)
