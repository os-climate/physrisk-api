import logging
import os
import pathlib
from datetime import timedelta

from dependency_injector import providers
from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from physrisk.container import Container
from werkzeug.middleware.proxy_fix import ProxyFix

from physrisk_api.app.override_providers import provide_s3_zarr_store

from .service import main


def create_app():
    dotenv_dir = os.environ.get("CREDENTIAL_DOTENV_DIR", os.getcwd())
    dotenv_path = pathlib.Path(dotenv_dir) / "credentials.env"
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path=dotenv_path, override=True)

    app = Flask(__name__)
    app.logger.setLevel(logging.INFO)
    app.logger.info("Starting physrisk_api...")

    container = Container()
    container.wire(modules=[".api"])
    # this is not needed but demonstrates how to override providers in physrisk Container.
    container.override_providers(zarr_store=providers.Singleton(provide_s3_zarr_store))
    # container.override_providers(config =
    # providers.Configuration(default={"zarr_sources": ["embedded", "hazard_test"]}))

    app.container = container
    _ = JWTManager(app)
    app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "not-to-be-used")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(weeks=1)

    CORS(app)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)
    # The 'main' blueprint should be the only one registered here.
    # All other routes or blueprints should register with 'main'.
    app.register_blueprint(main)

    return app
