"""API module."""
import logging

from flask_restx import Api

from frux_app_server import __version__

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


api = Api(prefix="/v1", version=__version__, validate=True)
# api.add_namespace(default_namespace, path='/hello')


@api.errorhandler
def handle_exception(error: Exception):
    """When an unhandled exception is raised"""
    message = "Error: " + getattr(error, 'message', str(error))
    return {'message': message}, getattr(error, 'code', 500)
