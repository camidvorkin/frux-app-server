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
            db.create_all()
        with app.test_client() as test_client:
            yield test_client
        with app.app_context():
            db.drop_all()


def read_graph_ql(client, query, exp_response):
    response = client.post('/graphql', json=query)
    assert response.status_code == 200
    assert json.loads(response.data.decode()) == exp_response


def test_get_all_users_empty_db(client):
    query = {
        'query': '''
            {
                allUsers {
                    edges {
                        node {
                            id
                        }
                    }
                }
            }'''
    }
    response = {"data": {"allUsers": {"edges": []}}}
    read_graph_ql(client, query, response)


def test_show_all_projects_empty_db(client):
    query = {
        'query': '''
            {
                allProjects {
                    edges {
                        node {
                            id
                        }
                    }
                }
            }'''
    }
    response = {"data": {"allProjects": {"edges": []}}}
    read_graph_ql(client, query, response)


def test_create_a_user(client):
    query = {
        'query': '''mutation {
            mutateUser(email: "pepe@gmail.com", name: "Pepe Suarez") {
                user {
                name,
                email,
                }
            }
        } '''
    }
    response = {
        "data": {
            "mutateUser": {"user": {"name": "Pepe Suarez", "email": "pepe@gmail.com"}}
        }
    }
    read_graph_ql(client, query, response)


def test_create_a_projecy(client):
    query = {
        'query': '''mutation {
                mutateProject(description: "Plant a tree", userId: 2, name: "Enviroment Proyect", goal: 50000){
                    project {
                    name,
                    description,
                    goal
                    }
                }
            }'''
    }
    response = {
        "data": {
            "mutateProject": {
                "project": {
                    "name": "Enviroment Proyect",
                    "description": "Plant a tree",
                    "goal": 50000,
                }
            }
        }
    }
    read_graph_ql(client, query, response)


# def test_delete_a_user(client):

# def test_root(client):
#     response = client.get("/")
#     assert response._status_code == 200

# def test_hello(client):
#     response = client.get("/v1/hello")
#     assert response._status_code == 200
#     assert json.loads(response.data).get("Say") == "Hello"

# def test_echo(client):
#     response = client.post("/v1/hello", json={"message": "Say hi"})
#     assert response._status_code == 200
#     assert json.loads(response.data).get("Echo") == "Say hi"
