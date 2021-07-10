import json
import os
import uuid

import responses
from behave import *  # pylint:disable=wildcard-import,unused-wildcard-import

# pylint:disable=undefined-variable,unused-argument,function-redefined


QUERY_PROFILE = '''
    {
        profile {
            walletAddress,
            wallet {
                internalId
            }
            seerProjects {
                edges {
                    node {
                        dbId,
                        name
                    }
                }
            }
        }
    }
'''

MUTATION_SEER_PROJECT = '''
    mutation SeerProject($idProject: Int!) {
        mutateSeerProject(idProject: $idProject) {
            dbId,
            currentState
        }
    }
'''

QUERY_PROJECT_STATE = '''
    query FindProject($dbId: Int!){
        project(dbId: $dbId) {
            currentState
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

    context.response = context.client.post(
        '/graphql',
        json={'query': QUERY_PROFILE},
        headers={'Authorization': f'Bearer {email}'},
    )
    assert context.response.status_code == 200

    res = json.loads(context.response.data.decode())
    assert res['data']['profile']['walletAddress'] is not None
    assert res['data']['profile']['wallet']['internalId'] is not None


@when(u'the owner of the project "{email}" enables the project for funding')
@responses.activate
def step_impl(context, email):
    mock_smart_contract_response('/project', {'txHash': str(uuid.uuid1())}, 200)

    context.response = context.client.post(
        '/graphql',
        json={
            'query': MUTATION_SEER_PROJECT,
            'variables': json.dumps({'idProject': context.last_project_id}),
        },
        headers={'Authorization': f'Bearer {email}'},
    )
    assert context.response.status_code == 200


@then(u'the project state is "{state}"')
def step_impl(context, state):
    context.response = context.client.post(
        '/graphql',
        json={
            'query': QUERY_PROJECT_STATE,
            'variables': json.dumps({'dbId': context.last_project_id}),
        },
        headers={'Authorization': f'Bearer {context.last_token}'},
    )
    assert context.response.status_code == 200

    res = json.loads(context.response.data.decode())
    assert res['data']['project']['currentState'] == state


@then(u'user "{email}" is supervising {n} project as seer')
def step_impl(context, email, n):
    context.response = context.client.post(
        '/graphql',
        json={'query': QUERY_PROFILE},
        headers={'Authorization': f'Bearer {email}'},
    )
    assert context.response.status_code == 200

    res = json.loads(context.response.data.decode())
    assert len(res['data']['profile']['seerProjects']['edges']) == int(n)
