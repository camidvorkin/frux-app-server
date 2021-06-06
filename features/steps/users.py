import json

from behave import *  # pylint:disable=wildcard-import,unused-wildcard-import
from commons import authenticate_user

from frux_app_server.models import User

ADMIN_TOKEN = 'AdminTestAuthToken'
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
    mutation NewUser($email: String!, $name: String!, $imagePath: String!, $latitude: String!, $longitude: String!) {
        mutateUser(email: $email, name: $name, imagePath: $imagePath, latitude: $latitude, longitude: $longitude) {
            name,
            email,
        }
    }
'''

MUTATION_UPDATE_USER = '''
    mutation UpdateUser($email: String!, $name: String!) {
        mutateUpdateUser(name: $name, email: $email) {
            name,
            email,
            dbId
        }
    }
'''

variables = {}
updated_variables = {}


@given('user is not registered')
def step_impl(context):
    pass


@when('user registers with name "{name}" and mail "{email}"')
def step_impl(context, name, email):
    variables['name'] = name
    variables['email'] = email


@when('image "{image_path}" and location "{location}"')
def step_impl(context, image_path, location):
    latitude, longitude = location.split(",")
    variables['imagePath'] = image_path
    variables['latitude'] = latitude
    variables['longitude'] = longitude
    context.response = context.client.post(
        '/graphql',
        json={'query': MUTATION_NEW_USER, 'variables': json.dumps(variables)},
    )


@then('user already registered with name "{name}" and mail "{email}"')
def step_impl(context, name, email):
    assert context.response.status_code == 200
    res = json.loads(context.response.data.decode())
    assert res == {"data": {"mutateUser": {"name": name, "email": email}}}


@when('users are listed')
def step_impl(context):
    context.response = context.client.post('/graphql', json={'query': QUERY_ALL_USERS})


@then('get a list of {n} users')
def step_impl(context, n):
    assert context.response.status_code == 200
    res = json.loads(context.response.data.decode())
    assert len(res['data']['allUsers']['edges']) == int(n)


@given(
    'user is already registered with name "{name}", mail "{email}", image "{image_path}" and location "{location}"'
)
def step_impl(context, name, email, image_path, location):
    latitude, longitude = location.split(",")
    user = User(
        name=name,
        email=email,
        image_path=image_path,
        latitude=latitude,
        longitude=longitude,
    )
    with context.app.app_context():
        context.db.session.add(user)
        context.db.session.commit()


@when(u'user with id {db_id} is listed')
def step_impl(context, db_id):
    variables['dbId'] = int(db_id)
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


@when('user update their username to "{name}" and their mail to "{email}"')
def step_impl(context, name, email):
    updated_variables['name'] = name
    updated_variables['email'] = email
    authenticate_user(context, email, ADMIN_TOKEN)

    context.response = context.client.post(
        '/graphql',
        json={
            'query': MUTATION_UPDATE_USER,
            'variables': json.dumps(updated_variables),
        },
        headers={'Authorization': f'Bearer {ADMIN_TOKEN}'},
    )


@then('the user\'s information change')
def step_impl(context):
    # Get updated project
    context.response = context.client.post(
        '/graphql',
        json={'query': QUERY_SINGLE_USER, 'variables': json.dumps({'dbId': 2})},
    )
    res = json.loads(context.response.data.decode())
    assert res['data']['user']['name'] == updated_variables['name']
    assert res['data']['user']['email'] == updated_variables['email']
