import json

from behave import *  # pylint:disable=wildcard-import,unused-wildcard-import

# pylint:disable=undefined-variable,unused-argument,function-redefined


QUERY_GET_PROJECT_FAVORITED_USERS = '''
    query FindProjectFavoritedUsers($dbId: Int!) {
        project(dbId: $dbId) {
            dbId
            favoritesFrom {
                edges {
                    node {
                        user {
                            email
                        }
                    }
                }
            }
        }
    }
'''

MUTATION_FAV_PROJECT = '''
    mutation FavProject($idProject: Int!) {
        mutateFavProject(idProject: $idProject) {
            userId,
            projectId
        }
    }
'''


MUTATION_UNFAV_PROJECT = '''
    mutation UnfavProject($idProject: Int!) {
        mutateUnfavProject(idProject: $idProject) {
            userId,
            projectId
        }
    }
'''


@when(u'users who favorited the project are listed')
def step_impl(context):
    variables = {'dbId': context.last_project_id}
    context.response = context.client.post(
        '/graphql',
        json={
            'query': QUERY_GET_PROJECT_FAVORITED_USERS,
            'variables': json.dumps(variables),
        },
        headers={'Authorization': f'Bearer {context.last_token}'},
    )
    assert context.response.status_code == 200


@then(u'get a list of {n} favorites')
def step_impl(context, n):
    res = json.loads(context.response.data.decode())
    assert len(res['data']['project']['favoritesFrom']['edges']) == int(n)


@given(u'the user favorited the project')
def step_impl(context):
    variables = {'idProject': context.last_project_id}
    context.response = context.client.post(
        '/graphql',
        json={'query': MUTATION_FAV_PROJECT, 'variables': json.dumps(variables)},
        headers={'Authorization': f'Bearer {context.last_token}'},
    )
    assert context.response.status_code == 200


@given(u'the user unfavorited the project')
def step_impl(context):
    variables = {'idProject': context.last_project_id}
    context.response = context.client.post(
        '/graphql',
        json={'query': MUTATION_UNFAV_PROJECT, 'variables': json.dumps(variables)},
        headers={'Authorization': f'Bearer {context.last_token}'},
    )
    assert context.response.status_code == 200
