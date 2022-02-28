"""Flask server"""

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from . import service


def create_app(debug=False):
    """create an application"""

    app = Flask(__name__)

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_host=1)
    app.register_blueprint(service.bp)

    return app
