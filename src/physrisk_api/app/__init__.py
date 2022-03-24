from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from .service import main


def create_app():
    app = Flask(__name__)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)
    # The 'main' blueprint should be the only one registered here.
    # All other routes or blueprints should register with 'main'.
    app.register_blueprint(main)

    return app
