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
            username,
            email,
            imagePath,
            description,
            isSeeder,
            isSponsor,
            isSeer
        }
    }
'''

MUTATION_NEW_USER = '''
    mutation NewUser($email: String!, $username: String!, $firstName: String!, $lastName: String!, $imagePath: String!, $latitude: String!, $longitude: String!) {
        mutateUser(email: $email, username: $username, firstName: $firstName, lastName: $lastName, imagePath: $imagePath, latitude: $latitude, longitude: $longitude) {
            username,
            email,
        }
    }
'''

MUTATION_UPDATE_USER = '''
    mutation UpdateUser($username: String!, $imagePath: String!) {
        mutateUpdateUser(username: $username, imagePath: $imagePath) {
            username,
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


@when(
    'user registers with username "{username}", name "{name}", lastname "{lastname}" and mail "{email}"'
)
def step_impl(context, username, name, lastname, email):
    variables['username'] = username
    variables['firstName'] = name
    variables['lastName'] = lastname
    variables['email'] = email


@when('image "{image_path}" with location "{location}" and address "{address}"')
def step_impl(context, image_path, location, address):
    latitude, longitude = location.split(",")
    variables['imagePath'] = image_path
    variables['latitude'] = latitude
    variables['longitude'] = longitude
    variables['address'] = address
    context.response = context.client.post(
        '/graphql',
        json={'query': MUTATION_NEW_USER, 'variables': json.dumps(variables)},
    )


@then('user already registered with username "{username}" and mail "{email}"')
def step_impl(context, username, email):
    assert context.response.status_code == 200
    res = json.loads(context.response.data.decode())
    assert res == {"data": {"mutateUser": {"username": username, "email": email}}}


@when('users are listed')
def step_impl(context):
    context.response = context.client.post('/graphql', json={'query': QUERY_ALL_USERS})


@then('get a list of {n} users')
def step_impl(context, n):
    assert context.response.status_code == 200
    res = json.loads(context.response.data.decode())
    assert len(res['data']['allUsers']['edges']) == int(n)


@given('user is already registered with mail "{email}"')
def step_impl(context, email):
    user = User(
        username="DefaultUserName",
        first_name="DefaultName",
        last_name="DefaultLastName",
        email=email,
        image_path="DefaultImage",
        latitude="00.0000",
        longitude="00.0000",
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


@then(u'get user with mail "{email}"')
def step_impl(context, email):
    assert context.response.status_code == 200
    res = json.loads(context.response.data.decode())
    assert res['data']['user']['email'] == email


@when('user update their username to "{username}" and their image to "{image_path}"')
def step_impl(context, username, image_path):
    updated_variables['username'] = username
    updated_variables['imagePath'] = image_path
    authenticate_user(context, image_path, ADMIN_TOKEN)

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
    assert res['data']['user']['username'] == updated_variables['username']
    assert res['data']['user']['imagePath'] == updated_variables['imagePath']


@then(u'user already registered with description "" and no role')
def step_impl(context):
    context.response = context.client.post(
        '/graphql',
        json={'query': QUERY_SINGLE_USER, 'variables': json.dumps({'dbId': 1})},
    )
    res = json.loads(context.response.data.decode())
    assert res['data']['user']['description'] == ""
    assert not res['data']['user']['isSeeder']
    assert not res['data']['user']['isSponsor']
    assert not res['data']['user']['isSeer']
