"""Sample test suite."""

import json
import logging
import tempfile

# pylint:disable=redefined-outer-name,protected-access
import pytest

from frux_app_server.app import create_app
from frux_app_server.models import db

logger = logging.getLogger(__name__)


@pytest.fixture
def client():
    with tempfile.NamedTemporaryFile() as dbf:
        app = create_app(test_db=f"sqlite:///{dbf.name}")
        with app.app_context():
            from flask_migrate import upgrade as _upgrade

            _upgrade()
        with app.test_client() as test_client:
            yield test_client
        with app.app_context():
            db.drop_all()


def test_root(client):
    response = client.get("/")
    assert response._status_code == 200


def test_hello(client):
    response = client.get("/v1/hello")
    assert response._status_code == 200
    assert json.loads(response.data).get("Say") == "Hello"


def test_echo(client):
    response = client.post("/v1/hello", json={"message": "Say hi"})
    assert response._status_code == 200
    assert json.loads(response.data).get("Echo") == "Say hi"
