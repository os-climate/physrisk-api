"""Entry point for the Physrisk API FastAPI application."""

import logging
import logging.config
from importlib.metadata import version
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import uvicorn

from physrisk_api.app.logging_config import LOGGING_CONFIG

from physrisk_api.app.routers import auth, container, asset, hazard, visualisation


logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(container.router)
app.include_router(asset.router)
app.include_router(hazard.router)
app.include_router(visualisation.router)


@app.get("/")
async def root():
    """Return a simple message to confirm the physrisk API is running."""
    logger.info("Physrisk API")
    return {"message": "Physrisk API"}


@app.get("/api/version")
async def get_version():
    """Return the version of the physrisk library in use."""
    return {"physrisk-lib": version("physrisk-lib")}


if __name__ == "__main__":
    # this is so that one can debug via, e.g. Python Debugger: Current File on main.py
    uvicorn.run(app, host="0.0.0.0", port=8000)
