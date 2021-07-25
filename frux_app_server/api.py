"""API module."""
import logging

import flask
from flask_restx import Api, Namespace, Resource

from frux_app_server import __version__

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


api = Api(version=__version__, validate=True)
ns = Namespace("", description="Default endpoint")


@api.errorhandler
def handle_exception(error: Exception):
    """When an unhandled exception is raised"""
    message = "Error: " + getattr(error, 'message', str(error))
    return {'message': message}, getattr(error, 'code', 500)


@ns.route('/health')
class health(Resource):
    """Health check endpoint"""

    def get(self):
        return flask.jsonify(status='ok')


api.add_namespace(ns, path='/')
