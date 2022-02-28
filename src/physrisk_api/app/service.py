from flask import Blueprint

bp = Blueprint("service", __name__, url_prefix="/")


@bp.get("/")
def home():
    return "Hello World!"
