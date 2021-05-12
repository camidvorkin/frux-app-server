import json

from behave import *  # pylint:disable=wildcard-import,unused-wildcard-import

# pylint:disable=undefined-variable,unused-argument,function-redefined


@then('operation is rejected with the message "{message}"')
def step_impl(context, message):
    res = json.loads(context.response.data.decode())
    assert res['errors'][0]['message'] == message
