import json

import responses
from behave import *  # pylint:disable=wildcard-import,unused-wildcard-import
from commons import mock_smart_contract_response

# pylint:disable=undefined-variable,unused-argument,function-redefined


QUERY_PROJECT_GOAL = '''
    query FindProject($dbId: Int!){
        project(dbId: $dbId) {
            goal
        }
    }
'''

MUTATION_NEW_STAGE = '''
    mutation NewProjectStage($description: String!, $title: String!, $goal: Float!, $idProject: Int!) {
        mutateProjectStage(description: $description, title: $title, goal: $goal, idProject: $idProject) {
            title
        }
    }
'''

MUTATION_COMPLETE_STAGE = '''
    mutation CompleteStage($idProject: Int!, $idStage: Int) {
        mutateCompleteStage(idProject: $idProject, idStage: $idStage) {
            dbId
            stages {
                edges {
                    node {
                        id
                        stageIndex
                        fundsReleased
                    }
                }
            }
        }
    }
'''


@given(u'a stage was created with title "{title}" and goal {n}')
def step_impl(context, title, n):
    variables = {
        'idProject': int(context.last_project_id),
        'description': title,
        'title': title,
        'goal': n,
    }
    context.response = context.client.post(
        '/graphql',
        json={'query': MUTATION_NEW_STAGE, 'variables': json.dumps(variables)},
        headers={'Authorization': f'Bearer {context.last_token}'},
    )

    assert context.response.status_code == 200


@when(u'the project is listed')
def step_impl(context):
    variables = {'dbId': context.last_project_id}
    context.response = context.client.post(
        '/graphql',
        json={'query': QUERY_PROJECT_GOAL, 'variables': json.dumps(variables)},
        headers={'Authorization': f'Bearer {context.last_token}'},
    )

    assert context.response.status_code == 200


@when(u'the seer {email} complete the stage {n}')
@responses.activate
def step_impl(context, email, n):
    mock_smart_contract_response(
        f'/project/{context.tx_hash}/stageId/{n}',
        {'reviewerId': context.seer_internal_id},
        200,
    )
    variables = {'idProject': context.last_project_id, 'idStage': n}
    context.response = context.client.post(
        '/graphql',
        json={'query': MUTATION_COMPLETE_STAGE, 'variables': json.dumps(variables)},
        headers={'Authorization': f'Bearer {context.last_token}'},
    )
    if json.loads(context.response.data.decode())['data']['mutateCompleteStage']:
        context.last_project_id = json.loads(context.response.data.decode())['data'][
            'mutateCompleteStage'
        ]['dbId']


@then(u'stages are complete up to stage {n}')
def step_impl(context, n):
    res = json.loads(context.response.data.decode())
    stages = res['data']['mutateCompleteStage']['stages']['edges']
    stages = sorted(
        [
            (stage['node']['stageIndex'], stage['node']['fundsReleased'])
            for stage in stages
        ],
        key=lambda stage: stage[0],
    )
    for i in range(int(n)):
        assert stages[i][1]
    for j in range(int(n), len(stages)):
        assert not stages[j][1]


@then(u'the project\'s goal is {n}')
def step_impl(context, n):
    res = json.loads(context.response.data.decode())
    assert res['data']['project']['goal'] == float(n)
