#!/usr/bin/env python
# -*- coding: utf-8 -*-

""" Flask server

"""

import os

from flask import Flask


try:
    from werkzeug.middleware.proxy_fix import ProxyFix
except ModuleNotFoundError: # werkzeug < 1.0.0
    from werkzeug.contrib.fixers import ProxyFix


class ReverseProxied(object):
    def __init__(self, app):
        self.app = ProxyFix(app, x_for=1, x_host=1)

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '')
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startwith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]
        return self.app(environ, start_response)


def create_app(debug=False):
    """create an application"""

    app = Flask(__name__)

    #app.wsgi_app = ReverseProxied(app.wsgi_app)

    # Set the secret key to some random bytes. Keep this really secret!
    app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

    # register the blueprints
    # A route script should group all the entry points (the one for the page but also the various services used to
    # update the components).
    # for route in os.listdir("routes"):
    #   if route.endswith(".py") and not route.startswith("__"):
    #     try:
    #       mod = importlib.import_module("routes.{}".format(route[:-3]))
    #       app.register_blueprint(mod.bp)
    #     except Exception as err:
    #       print("Error with route {}".format(route))
    #       print(err)

    return app
