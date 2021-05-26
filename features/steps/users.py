import json

from behave import *  # pylint:disable=wildcard-import,unused-wildcard-import

from frux_app_server.models import User

# pylint:disable=undefined-variable,unused-argument,function-redefined

QUERY_ALL_USERS = '''
    {
        allUsers {
            edges {
                node {
                    id
                }
            }
        }
    }
'''

QUERY_PROFILE = '''
    {
        profile {
            id,
            email
        }
    }
'''

QUERY_SINGLE_USER = '''
    query FindUser($dbId: Int!){
        user(dbId: $dbId) {
            name,
            email
        }
    }
'''

MUTATION_NEW_USER = '''
    mutation NewUser($email: String!, $name: String!) {
        mutateUser(email: $email, name: $name) {
            user {
                name,
                email,
            }
        }
    }
'''


@given('user is not registered')
def step_impl(context):
    pass


@when('user registers with name "{name}" and mail "{email}"')
def step_impl(context, name, email):
    variables = {'email': email, 'name': name}
    context.response = context.client.post(
        '/graphql',
        json={'query': MUTATION_NEW_USER, 'variables': json.dumps(variables)},
    )


@then('user already registered with name "{name}" and mail "{email}"')
def step_impl(context, name, email):
    assert context.response.status_code == 200
    res = json.loads(context.response.data.decode())
    assert res == {"data": {"mutateUser": {"user": {"name": name, "email": email}}}}


@when('users are listed')
def step_impl(context):
    context.response = context.client.post('/graphql', json={'query': QUERY_ALL_USERS})


@then('get a list of {n} users')
def step_impl(context, n):
    assert context.response.status_code == 200
    res = json.loads(context.response.data.decode())
    assert len(res['data']['allUsers']['edges']) == int(n)


@given('user is already registered with name "{name}" and mail "{email}"')
def step_impl(context, name, email):
    user = User(name=name, email=email)
    with context.app.app_context():
        context.db.session.add(user)
        context.db.session.commit()


@when(u'user with id {db_id} is listed')
def step_impl(context, db_id):
    variables = {'dbId': int(db_id)}
    context.response = context.client.post(
        '/graphql',
        json={'query': QUERY_SINGLE_USER, 'variables': json.dumps(variables)},
    )


@then(u'get user with name "{name}" and mail "{email}"')
def step_impl(context, name, email):
    assert context.response.status_code == 200
    res = json.loads(context.response.data.decode())
    assert res['data']['user']['email'] == email
    assert res['data']['user']['name'] == name
