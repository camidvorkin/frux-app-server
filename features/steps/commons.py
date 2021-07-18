import json
import os

import responses
from behave import *  # pylint:disable=wildcard-import,unused-wildcard-import

from frux_app_server.models import Admin, Category

# pylint:disable=undefined-variable,unused-argument,function-redefined


@then('operation is rejected with the message "{message}"')
def step_impl(context, message):
    res = json.loads(context.response.data.decode())
    print(res)
    assert res['errors'][0]['message'] == message


def authenticate_user(context, email, token):
    admin = Admin(email=email, token=token)
    context.last_token = email
    with context.app.app_context():
        context.db.session.add(admin)
        context.db.session.commit()


@given('user with mail "{email}" is authenticated')
def step_impl(context, email):
    authenticate_user(context, email, email)


@given('default categories are in the database')
def step_impl(context):
    categories = [
        'Arts',
        'Comics & Illustration',
        'Design & Tech',
        'Film',
        'Food & Craft',
        'Games',
        'Music',
        'Publishing',
        'Other',
    ]
    with context.app.app_context():
        for category in categories:
            context.db.session.add(Category(name=category))
        context.db.session.commit()


def mock_smart_contract_response(path, content, status_code, verb=responses.POST):
    url = os.environ.get('FRUX_SC_URL', 'http://localhost:3000')
    responses.add(verb, url + path, body=json.dumps(content), status=status_code)
