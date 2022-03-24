from flask import Blueprint

from .api import api

main = Blueprint("main", __name__, url_prefix="/")

# Register all routes or blueprints with the 'main' blueprint.
main.register_blueprint(api)


@main.get("/")
def home():
    return "Hello World!"
