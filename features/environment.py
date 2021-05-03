import tempfile

from behave import fixture, use_fixture

from frux_app_server.app import create_app
from frux_app_server.models import db

# pylint:disable=unused-argument


@fixture
def app_client(context, *args, **kwargs):
    with tempfile.NamedTemporaryFile() as dbf:
        app = create_app(test_db=f"sqlite:///{dbf.name}")
        with app.app_context():
            db.create_all()
        with app.test_client() as test_client:
            context.client = test_client
            context.db = db
            yield context.client
        with app.app_context():
            db.drop_all()


def before_scenario(context, feature):
    # Restart application per-scenario
    use_fixture(app_client, context)
