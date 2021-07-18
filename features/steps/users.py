import json

from behave import *  # pylint:disable=wildcard-import,unused-wildcard-import
from commons import authenticate_user

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
            username,
            email,
            imagePath,
            description,
            isSeer
        }
    }
'''

MUTATION_NEW_USER = '''
    mutation NewUser($email: String!, $username: String!, $firstName: String!, $lastName: String!, $imagePath: String!, $latitude: String!, $longitude: String!, $interests: [String!]!) {
        mutateUser(email: $email, username: $username, firstName: $firstName, lastName: $lastName, imagePath: $imagePath, latitude: $latitude, longitude: $longitude, interests: $interests) {
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

MUTATION_UPDATE_USER_LOCATION = '''
    mutation UpdateUser($latitude: String!, $longitude: String!) {
        mutateUpdateUser(latitude: $latitude, longitude: $longitude) {
            latitude,
            longitude
        }
    }
'''

MUTATION_UPDATE_USER_INTERESTS = '''
    mutation UpdateUser($interests: [String!]!) {
        mutateUpdateUser(interests: $interests) {
            interests {
                edges {
                    node {
                        name
                    }
                }
            }
        }
    }
'''

MUTATION_SET_SEER = '''
    mutation {
        mutateSetSeer {
            email,
            isSeer,
            wallet {
                internalId
            }
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
    variables['interests'] = variables.get('interests', [])
    context.response = context.client.post(
        '/graphql',
        json={'query': MUTATION_NEW_USER, 'variables': json.dumps(variables)},
    )


@when('interests "{interests}"')
def step_impl(context, interests):
    variables['interests'] = interests.split(',')


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
    authenticate_user(context, email, email)
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


@when('user updates their username to "{username}" and their image to "{image_path}"')
def step_impl(context, username, image_path):
    updated_variables['username'] = username
    updated_variables['imagePath'] = image_path

    context.response = context.client.post(
        '/graphql',
        json={
            'query': MUTATION_UPDATE_USER,
            'variables': json.dumps(updated_variables),
        },
        headers={'Authorization': f'Bearer {context.last_token}'},
    )


@then(
    'the user\'s username changes to "{username}" and their image changes to "{image_path}"'
)
def step_impl(context, username, image_path):
    # Get updated project
    context.response = context.client.post(
        '/graphql',
        json={'query': QUERY_SINGLE_USER, 'variables': json.dumps({'dbId': 1})},
    )
    res = json.loads(context.response.data.decode())
    assert res['data']['user']['username'] == username
    assert res['data']['user']['imagePath'] == image_path


@then(u'user already registered with description "" and no role')
def step_impl(context):
    context.response = context.client.post(
        '/graphql',
        json={'query': QUERY_SINGLE_USER, 'variables': json.dumps({'dbId': 1})},
    )
    res = json.loads(context.response.data.decode())
    assert res['data']['user']['description'] == ""
    assert not res['data']['user']['isSeer']


@then(u'registration is successful')
def step_impl(context):
    assert context.response.status_code == 200
    res = json.loads(context.response.data.decode())
    assert res['data']['mutateUser']['email'] == variables['email']


@given(u'user with mail "{email}" has a seer role')
def step_impl(context, email):
    context.response = context.client.post(
        '/graphql',
        json={'query': MUTATION_SET_SEER, 'variables': json.dumps({'dbId': 1})},
        headers={'Authorization': f'Bearer {email}'},
    )
    assert context.response.status_code == 200

    res = json.loads(context.response.data.decode())
    assert res['data']['mutateSetSeer']['isSeer']


@when(u'user updates their latitude to "{latitude}" and longitude to "{longitude}"')
def step_impl(context, latitude, longitude):
    updated_variables['latitude'] = latitude
    updated_variables['longitude'] = longitude

    context.response = context.client.post(
        '/graphql',
        json={
            'query': MUTATION_UPDATE_USER_LOCATION,
            'variables': json.dumps(updated_variables),
        },
        headers={'Authorization': f'Bearer {context.last_token}'},
    )


@then(u'the user\'s latitude changes to "{latitude}" and longitude to "{longitude}"')
def step_impl(context, latitude, longitude):
    assert context.response.status_code == 200

    res = json.loads(context.response.data.decode())
    assert res['data']['mutateUpdateUser']['latitude'] == latitude
    assert res['data']['mutateUpdateUser']['longitude'] == longitude


@when(u'user updates their interests to "{interests}"')
def step_impl(context, interests):
    mutation_variables = {'interests': interests.split(',')}
    context.response = context.client.post(
        '/graphql',
        json={'query': MUTATION_UPDATE_USER_INTERESTS, 'variables': mutation_variables},
        headers={'Authorization': f'Bearer {context.last_token}'},
    )


@then(u'the user\'s new interests are "{interests}"')
def step_impl(context, interests):
    assert context.response.status_code == 200

    res = json.loads(context.response.data.decode())

    for h in res['data']['mutateUpdateUser']['interests']['edges']:
        assert h['node']['name'] in interests.split(',')

    assert len(res['data']['mutateUpdateUser']['interests']['edges']) == len(
        interests.split(',')
    )
