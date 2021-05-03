import json

from behave import *  # pylint:disable=wildcard-import,unused-wildcard-import

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


@given('usuario no esta registrado')
def step_impl(context):
    pass


@given('usuario ya se encuentra registrado con nombre "{name}" y mail "{email}"')
@when('usuario se registra con nombre "{name}" y mail "{email}"')
def step_impl(context, name, email):
    variables = {'email': email, 'name': name}
    context.response = context.client.post(
        '/graphql',
        json={'query': MUTATION_NEW_USER, 'variables': json.dumps(variables)},
    )


@then('usuario registrado con nombre "{name}" y mail "{email}"')
def step_impl(context, name, email):
    assert context.response.status_code == 200
    res = json.loads(context.response.data.decode())
    assert res == {"data": {"mutateUser": {"user": {"name": name, "email": email}}}}


@then('se rechaza la operacion con el mensaje "{message}"')
def step_impl(context, message):
    res = json.loads(context.response.data.decode())
    assert res['errors'][0]['message'] == message


@when('se listan todos los usuarios')
def step_impl(context):
    context.response = context.client.post('/graphql', json={'query': QUERY_ALL_USERS})


@then('se obtienen {n} usuarios')
def step_impl(context, n):
    assert context.response.status_code == 200
    res = json.loads(context.response.data.decode())
    assert len(res['data']['allUsers']['edges']) == int(n)