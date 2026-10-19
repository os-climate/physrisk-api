"""Entry point for the Physrisk API FastAPI application."""

import gc
import logging
import logging.config
import os
from importlib.metadata import version

import psutil
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from physrisk_api.app.logging_config import LOGGING_CONFIG
from physrisk_api.app.routers import asset, auth, container, hazard, visualisation

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


@app.get("/api/memory")
async def get_memory():
    """Return current process RSS memory usage in MB."""
    gc.collect()
    rss_mb = psutil.Process(os.getpid()).memory_info().rss / 1e6
    return {"rss_mb": round(rss_mb, 1)}


if __name__ == "__main__":
    # this is so that one can debug via, e.g. Python Debugger: Current File on main.py
    uvicorn.run(app, host="0.0.0.0", port=8000)
