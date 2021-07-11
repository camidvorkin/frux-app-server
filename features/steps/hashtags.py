import json

from behave import *  # pylint:disable=wildcard-import,unused-wildcard-import

# pylint:disable=undefined-variable,unused-argument,function-redefined

QUERY_ALL_HASHTAGS = '''
{
    allHashtags {
        edges {
            node {
                hashtag
            }
        }
    }
}
'''

MUTATION_NEW_PROJECT_WITH_HASHTAGS = '''
    mutation NewProject($description: String!, $name: String!, $goal: Int!, $hashtags: [String], $deadline: String!) {
        mutateProject(name: $name, description: $description, goal: $goal, hashtags: $hashtags, deadline: $deadline) {
            name,
            dbId
        }
    }
'''

MUTATION_UPDATE_PROJECT_WITH_HASHTAGS = '''
    mutation UpdateProject($dbId: Int!, $hashtags: [String]) {
        mutateUpdateProject(idProject: $dbId, hashtags: $hashtags) {
            name,
            dbId
        }
    }
'''

QUERY_GET_PROJECT_HASHTAGS = '''
    query FindProject($dbId: Int!) {
        project(dbId: $dbId) {
            dbId
            hashtags {
                edges {
                    node {
                        hashtag
                    }
                }
            }
        }
    }
'''


@given(u'a new project was created by the user with hashtags "{hashtags}"')
def step_impl(context, hashtags):
    variables = {
        'hashtags': hashtags.split(","),
        'description': "descriptionTest",
        'name': "nameTest",
        'goal': 1,
        'deadline': "2022-1-1",
    }
    context.response = context.client.post(
        '/graphql',
        json={
            'query': MUTATION_NEW_PROJECT_WITH_HASHTAGS,
            'variables': json.dumps(variables),
        },
        headers={'Authorization': f'Bearer {context.last_token}'},
    )
    context.last_project_id = json.loads(context.response.data.decode())['data'][
        'mutateProject'
    ]['dbId']


@when('hashtags are listed')
@when(u'hashtags and projects are counted')
def step_impl(context):
    context.response = context.client.post(
        '/graphql', json={'query': QUERY_ALL_HASHTAGS}
    )


@then('get a list of {n} hashtags')
def step_impl(context, n):
    res = json.loads(context.response.data.decode())
    assert len(res['data']['allHashtags']['edges']) == int(n)


@when('the project\'s hashtags are updated to "{hashtags}"')
def step_impl(context, hashtags):
    variables = {'hashtags': hashtags.split(","), 'dbId': context.last_project_id}
    context.response = context.client.post(
        '/graphql',
        json={
            'query': MUTATION_UPDATE_PROJECT_WITH_HASHTAGS,
            'variables': json.dumps(variables),
        },
        headers={'Authorization': f'Bearer {context.last_token}'},
    )


@then('the project has "{hashtags}" as hashtags')
def step_impl(context, hashtags):
    variables = {}
    variables['dbId'] = context.last_project_id

    context.response = context.client.post(
        '/graphql',
        json={'query': QUERY_GET_PROJECT_HASHTAGS, 'variables': json.dumps(variables)},
        headers={'Authorization': f'Bearer {context.last_token}'},
    )

    res = json.loads(context.response.data.decode())

    for h in res['data']['project']['hashtags']['edges']:
        assert h['node']['hashtag'] in hashtags.split(',')

    assert len(res['data']['project']['hashtags']['edges']) == len(hashtags.split(','))
