import json

from behave import *  # pylint:disable=wildcard-import,unused-wildcard-import

# pylint:disable=undefined-variable,unused-argument,function-redefined

QUERY_ALL_HASHTAGS = '''
{
    allHashtags {
        edges {
            node {
                hashtag,
                idProject
            }
        }
    }
}
'''

MUTATION_NEW_PROJECT_WITH_HASHTAGS = '''
    mutation NewProject($description: String!, $userId: Int!, $name: String!, $goal: Int!, $hashtags: [String]) {
        mutateProject(userId: $userId, name: $name, description: $description, goal: $goal, hashtags: $hashtags) {
            project {
                name
            }
        }
    }
'''


@given(u'a new project valid project with hashtags "{hashtags}"')
def step_impl(context, hashtags):
    variables = {
        'hashtags': hashtags.split(","),
        'description': "descriptionTest",
        'userId': 1,
        'name': "nameTest",
        'goal': 1,
    }
    context.response = context.client.post(
        '/graphql',
        json={
            'query': MUTATION_NEW_PROJECT_WITH_HASHTAGS,
            'variables': json.dumps(variables),
        },
    )


@when('hashtags are listed')
@when(u'hashtags and projects are counted')
def step_impl(context):
    context.response = context.client.post(
        '/graphql', json={'query': QUERY_ALL_HASHTAGS}
    )


@then('get a list of {n} hashtags')
def step_impl(context, n):
    assert context.response.status_code == 200
    res = json.loads(context.response.data.decode())
    assert len(res['data']['allHashtags']['edges']) == int(n)


@then('get {n} hashtags and {m} projects')
def step_impl(context, n, m):
    assert context.response.status_code == 200
    res = json.loads(context.response.data.decode())
    hashtags, projects = set(), set()
    for hashtag in res['data']['allHashtags']['edges']:
        hashtags.add(hashtag['node']['hashtag'])
        projects.add(hashtag['node']['idProject'])
    assert len(hashtags) == int(n)
    assert len(projects) == int(m)
