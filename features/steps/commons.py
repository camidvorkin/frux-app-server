import json

from behave import *  # pylint:disable=wildcard-import,unused-wildcard-import

from frux_app_server.models import Admin

# pylint:disable=undefined-variable,unused-argument,function-redefined

ADMIN_TOKEN = 'AdminTestAuthToken'


@then('operation is rejected with the message "{message}"')
def step_impl(context, message):
    res = json.loads(context.response.data.decode())
    print(res['errors'][0]['message'])
    print(message)
    assert res['errors'][0]['message'] == message


def authenticate_user(context, email, token=ADMIN_TOKEN):
    admin = Admin(email=email, token=token)
    with context.app.app_context():
        context.db.session.add(admin)
        context.db.session.commit()


@given('user with mail "{email}" is authenticated')
def step_impl(context, email):
    authenticate_user(context, email, ADMIN_TOKEN)
