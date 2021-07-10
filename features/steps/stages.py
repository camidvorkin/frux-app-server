import json

from behave import *  # pylint:disable=wildcard-import,unused-wildcard-import

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


@then(u'the project\'s goal is {n}')
def step_impl(context, n):
    res = json.loads(context.response.data.decode())
    assert res['data']['project']['goal'] == float(n)
