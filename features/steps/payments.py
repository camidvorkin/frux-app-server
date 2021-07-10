import json
import os
import uuid

import responses
from behave import *  # pylint:disable=wildcard-import,unused-wildcard-import

# pylint:disable=undefined-variable,unused-argument,function-redefined


QUERY_PROFILE = '''
    {
        profile {
            walletAddress
        }
    }
'''


def mock_smart_contract_response(path, content, status_code, verb=responses.POST):
    url = os.environ.get('FRUX_SC_URL', 'http://localhost:3000')
    responses.add(verb, url + path, body=json.dumps(content), status=status_code)


@when(u'user views their profile')
@responses.activate
def step_impl(context):
    if 'wallets' not in context:
        context.wallets = {}

    context.wallets[context.last_token] = {
        'address': str(uuid.uuid1()),
        'id': str(uuid.uuid1()),
    }

    mock_smart_contract_response('/wallet', context.wallets[context.last_token], 200)

    context.response = context.client.post(
        '/graphql',
        json={'query': QUERY_PROFILE},
        headers={'Authorization': f'Bearer {context.last_token}'},
    )

    assert context.response.status_code == 200


@then(u'it should include their wallet\'s address')
def step_impl(context):
    res = json.loads(context.response.data.decode())
    assert res['data']['profile']['walletAddress'] is not None


@given(u'user with mail "{email}" is authenticated and has a wallet')
def step_impl(context, email):
    context.execute_steps(
        u"""
        given user with mail "{email}" is authenticated
        when user views their profile
    """.format(
            email=email
        )
    )
