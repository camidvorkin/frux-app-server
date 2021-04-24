"""Flask api."""
import logging
from pathlib import Path

from flask import Flask
from flask_cors import CORS
from flask_graphql import GraphQLView
from flask_migrate import Migrate
from werkzeug.middleware.proxy_fix import ProxyFix

from frux_app_server.api import api
from frux_app_server.cfg import config
from frux_app_server.models import db

from .schema import schema

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def fix_dialect(s):
    if s.startswith("postgres://"):
        s = s.replace("postgres://", "postgresql://")
    s = s.replace("postgresql://", "postgresql+psycopg2://")
    return s


def create_app(test_db=None):
    """creates a new app instance"""
    new_app = Flask(__name__)
    new_app.config["SQLALCHEMY_DATABASE_URI"] = config.database.url(
        default=test_db or "sqlite:///frux_app_server.db", cast=fix_dialect
    )
    new_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    new_app.config["ERROR_404_HELP"] = False
    db.init_app(new_app)
    api.init_app(new_app)

    new_app.add_url_rule(
        '/graphql',
        view_func=GraphQLView.as_view(
            'graphql', schema=schema, graphiql=True  # for having the GraphiQL interface
        ),
    )

    Migrate(new_app, db, directory=Path(__file__).parent / "migrations")
    new_app.wsgi_app = ProxyFix(
        new_app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1
    )  # remove after flask-restx > 0.2.0 is released
    # https://github.com/python-restx/flask-restx/issues/230
    CORS(new_app)
    return new_app
