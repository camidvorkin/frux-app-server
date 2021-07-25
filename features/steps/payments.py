import json
import os
import uuid

import requests
import responses
from behave import *  # pylint:disable=wildcard-import,unused-wildcard-import
from commons import mock_smart_contract_response

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
            currentState,
            goal,
            seer {
                email
                wallet{
                    internalId
                }
            }
        }
    }
'''

MUTATION_INVEST_PROJECT = '''
    mutation InvestProject($idProject: Int!, $investedAmount: Float!) {
        mutateInvestProject(idProject: $idProject, investedAmount: $investedAmount) {
            userId,
            investedAmount
        }
    }
'''

MUTATION_WITHDRAW_PROJECT = '''
    mutation WithdrawFunds($idProject: Int!, $withdrawAmount: Float!) {
        mutateWithdrawFunds(idProject: $idProject, withdrawAmount: $withdrawAmount) {
            userId,
            investedAmount
        }
    }
'''

QUERY_PROJECT_STATE = '''
    query FindProject($dbId: Int!){
        project(dbId: $dbId) {
            currentState,
            investorCount,
            amountCollected
        }
    }
'''


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
@when(u'user with mail "{email}" is authenticated and has a wallet')
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
@given(u'the owner of the project "{email}" enabled the project for funding')
@responses.activate
def step_impl(context, email):
    context.tx_hash = str(uuid.uuid1())
    mock_smart_contract_response('/project', {'txHash': context.tx_hash}, 200)

    context.response = context.client.post(
        '/graphql',
        json={
            'query': MUTATION_SEER_PROJECT,
            'variables': json.dumps({'idProject': context.last_project_id}),
        },
        headers={'Authorization': f'Bearer {email}'},
    )
    assert context.response.status_code == 200
    res = json.loads(context.response.data.decode())
    context.project_goal = int(res['data']['mutateSeerProject']['goal'])
    context.seer_internal_id = res['data']['mutateSeerProject']['seer']['wallet'][
        'internalId'
    ]


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


@given(u'user "{email}" invested {n}')
@when(u'user "{email}" invests {n}')
@responses.activate
def step_impl(context, email, n):
    n = int(n)
    invested = min(context.project_goal, n)
    context.project_goal -= invested

    if 'project_investments' not in context:
        context.project_investments = {}
    context.project_investments[email] = (
        context.project_investments.get(email, 0) + invested
    )

    mock_smart_contract_response(
        f'/project/{context.tx_hash}',
        {'value': {'hex': hex(invested * (10 ** 18))}},
        200,
    )

    variables = {'idProject': context.last_project_id, 'investedAmount': n}
    context.response = context.client.post(
        '/graphql',
        json={'query': MUTATION_INVEST_PROJECT, 'variables': json.dumps(variables)},
        headers={'Authorization': f'Bearer {email}'},
    )
    assert context.response.status_code == 200


@when(u'user "{email}" does not have enough funds but invests {n}')
@responses.activate
def step_impl(context, email, n):
    n = int(n)
    invested = min(context.project_goal, n)
    context.project_goal -= invested

    if 'project_investments' not in context:
        context.project_investments = {}
    context.project_investments[email] = (
        context.project_investments.get(email, 0) + invested
    )

    mock_smart_contract_response(
        f'/project/{context.tx_hash}', {'code': 'INSUFFICIENT_FUNDS'}, 500,
    )

    variables = {'idProject': context.last_project_id, 'investedAmount': n}
    context.response = context.client.post(
        '/graphql',
        json={'query': MUTATION_INVEST_PROJECT, 'variables': json.dumps(variables)},
        headers={'Authorization': f'Bearer {email}'},
    )
    assert context.response.status_code == 200


@when(u'payment service is down but user "{email}" invests {n}')
@responses.activate
def step_impl(context, email, n):
    n = int(n)
    invested = min(context.project_goal, n)
    context.project_goal -= invested

    if 'project_investments' not in context:
        context.project_investments = {}
    context.project_investments[email] = (
        context.project_investments.get(email, 0) + invested
    )

    url = os.environ.get('FRUX_SC_URL', 'http://localhost:3000')
    responses.add(
        responses.POST,
        url + f'/project/{context.tx_hash}',
        body=requests.ConnectionError(),
    )

    variables = {'idProject': context.last_project_id, 'investedAmount': n}
    context.response = context.client.post(
        '/graphql',
        json={'query': MUTATION_INVEST_PROJECT, 'variables': json.dumps(variables)},
        headers={'Authorization': f'Bearer {email}'},
    )
    assert context.response.status_code == 200


@then(
    u'the project invested ammount is {invested_amount} and has {investor_count} investors'
)
def step_impl(context, invested_amount, investor_count):
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
    assert res['data']['project']['amountCollected'] == float(invested_amount)
    assert res['data']['project']['investorCount'] == int(investor_count)


@when(u'user "{email}" withdraws {n}')
@responses.activate
def step_impl(context, email, n):
    n = int(n)
    if 'project_investments' not in context:
        context.project_investments = {}
    context.project_investments[email] = max(
        context.project_investments.get(email, 0) - n, 0
    )

    mock_smart_contract_response(
        f'/project/{context.tx_hash}/withdraw', {}, 200,
    )

    variables = {'idProject': context.last_project_id, 'withdrawAmount': n}
    context.response = context.client.post(
        '/graphql',
        json={'query': MUTATION_WITHDRAW_PROJECT, 'variables': json.dumps(variables)},
        headers={'Authorization': f'Bearer {email}'},
    )
    assert context.response.status_code == 200
