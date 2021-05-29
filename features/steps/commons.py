import json

from behave import *  # pylint:disable=wildcard-import,unused-wildcard-import

from frux_app_server.models import Admin

# pylint:disable=undefined-variable,unused-argument,function-redefined

ADMIN_TOKEN = 'AdminTestAuthToken'


@then('operation is rejected with the message "{message}"')
def step_impl(context, message):
    res = json.loads(context.response.data.decode())
    assert res['errors'][0]['message'] == message


@given('user with mail "{email}" is authenticated')
def step_impl(context, email):
    admin = Admin(email=email, token=ADMIN_TOKEN)
    with context.app.app_context():
        context.db.session.add(admin)
        context.db.session.commit()
