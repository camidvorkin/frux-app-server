import json

from behave import *  # pylint:disable=wildcard-import,unused-wildcard-import
from commons import authenticate_user

# pylint:disable=undefined-variable,unused-argument,function-redefined


ADMIN_TOKEN = 'AdminTestAuthToken'

QUERY_ALL_PROJECT = '''
    {
        allProjects {
            edges {
                node {
                    id
                }
            }
        }
    }
'''

QUERY_ALL_PROJECT_FILTERS = '''
    query SearchProjectByName($name: String!){
        allProjects(filters: {name: $name}) {
            edges {
                node {
                    id
                }
            }
        }
    }
'''

MUTATION_NEW_PROJECT = '''
    mutation NewProject($description: String!, $name: String!, $goal: Int!, $category: String, $hashtags: [String], $deadline: String!) {
        mutateProject(name: $name, description: $description, goal: $goal, category: $category, hashtags: $hashtags, deadline: $deadline) {
            name,
            description,
            goal,
            categoryName,
            currentState
        }
    }
'''

MUTATION_NEW_PROJECT_SIMPLE = '''
    mutation NewProject($description: String!, $name: String!, $goal: Int!, $deadline: String!) {
        mutateProject(name: $name, description: $description, goal: $goal, deadline: $deadline) {
            name,
            description,
            goal,
            dbId
        }
    }
'''

QUERY_SINGLE_PROJECT = '''
    query FindProject($dbId: Int!){
        project(dbId: $dbId) {
            name
            description
            seer {
                email
            }
        }
    }
'''

MUTATION_UPDATE_PROJECT = '''
    mutation UpdateProject($idProject: Int!, $description: String!, $name: String!) {
        mutateUpdateProject(idProject: $idProject, name: $name, description: $description) {
            name,
            description,
        }
    }
'''

MUTATION_CANCEL_PROJECT = '''
    mutation CancelProject($idProject: Int!) {
        mutateCancelProject(idProject: $idProject) {
            name,
            currentState,
        }
    }
'''

variables = {}
updated_variables = {}


@given('a new project')
def step_impl(context):
    pass


@given('project "{name}" has already been created for user')
@when('user create a project "{name}"')
def step_impl(context, name):
    variables['name'] = name
    variables['deadline'] = "2022-1-1"
    variables['category'] = None
    variables['stage'] = None


@given('is about "{description}"')
@when('is about "{description}"')
def step_impl(context, description):
    variables['description'] = description


@given('the category is "{category}"')
@when('the category is "{category}"')
def step_impl(context, category):
    variables['category'] = category


@given('the stage is "{stage}"')
@when('the stage is "{stage}"')
def step_impl(context, stage):
    variables['stage'] = stage


@when('hashtags "{hashtags}"')
def step_impl(context, hashtags):
    h = hashtags.split(",")
    variables['hashtags'] = h


@given('the total amount to be collected is {goal}')
@when('the total amount to be collected is {goal}')
def step_impl(context, goal):
    variables['goal'] = int(goal)
    context.response = context.client.post(
        '/graphql',
        json={'query': MUTATION_NEW_PROJECT, 'variables': json.dumps(variables)},
        headers={'Authorization': f'Bearer {context.last_token}'},
    )


@given('an old project')
def step_impl(context):
    variables['name'] = "Old project"
    variables['stage'] = "CREATED"
    variables['goal'] = 1
    variables['hashtags'] = []
    variables['description'] = "Old project"
    authenticate_user(context, "olduser@gmail.com", "olduser@gmail.com")

    context.response = context.client.post(
        '/graphql',
        json={'query': MUTATION_NEW_PROJECT, 'variables': json.dumps(variables)},
        headers={'Authorization': f'Bearer {context.last_token}'},
    )
    context.email = "olduser@gmail.com"


@when('projects are listed')
def step_impl(context):
    context.response = context.client.post(
        '/graphql', json={'query': QUERY_ALL_PROJECT}
    )


@then(
    'the project "{name}", description "{description}", category "{category}", state "{state}" and goal {goal} is created correctly'
)
def step_impl(context, name, description, goal, category, state):
    res = json.loads(context.response.data.decode())
    assert res == {
        "data": {
            "mutateProject": {
                "name": str(name),
                "description": str(description),
                "goal": int(goal),
                "categoryName": str(category),
                "currentState": str(state),
            }
        }
    }


@then('get a list of {n} projects')
def step_impl(context, n):
    res = json.loads(context.response.data.decode())
    assert len(res['data']['allProjects']['edges']) == int(n)


@when('projects are listed filtering by name "{name}"')
def step_impl(context, name):
    context.response = context.client.post(
        '/graphql',
        json={
            'query': QUERY_ALL_PROJECT_FILTERS,
            'variables': json.dumps({'name': name}),
        },
    )


@when('the project is cancelled')
def step_impl(context):
    print(context.email)
    context.response = context.client.post(
        '/graphql',
        json={
            'query': MUTATION_CANCEL_PROJECT,
            'variables': json.dumps({'idProject': int(1)}),
        },
        headers={'Authorization': f'Bearer {context.email}'},
    )


@when('project with id {db_id} is listed')
def step_impl(context, db_id):
    context.response = context.client.post(
        '/graphql',
        json={
            'query': QUERY_SINGLE_PROJECT,
            'variables': json.dumps({'dbId': int(db_id)}),
        },
    )


@when('project new name is "{y}"')
def step_impl(context, y):
    updated_variables['name'] = y


@when('project new description is "{y}"')
def step_impl(context, y):
    updated_variables['description'] = y


@then('the project\'s information change')
def step_impl(context):
    # Mutation
    updated_variables['idProject'] = 1
    context.response = context.client.post(
        '/graphql',
        json={
            'query': MUTATION_UPDATE_PROJECT,
            'variables': json.dumps(updated_variables),
        },
        headers={'Authorization': f'Bearer {context.last_token}'},
    )
    # Get updated project
    context.response = context.client.post(
        '/graphql',
        json={
            'query': QUERY_SINGLE_PROJECT,
            'variables': json.dumps({'dbId': int(1)}),
        },
    )
    res = json.loads(context.response.data.decode())
    assert res['data']['project']['description'] == updated_variables['description']
    assert res['data']['project']['name'] == updated_variables['name']


@then(u'the seer of the project is "{email}"')
@when(u'the seer of the project is "{email}"')
def step_impl(context, email):
    context.response = context.client.post(
        '/graphql',
        json={
            'query': QUERY_SINGLE_PROJECT,
            'variables': json.dumps({'dbId': int(1)}),
        },
    )
    assert context.response.status_code == 200
    res = json.loads(context.response.data.decode())
    assert res['data']['project']['seer']['email'] == email


@then('get project with name "{name}" and description "{description}"')
def step_impl(context, name, description):
    assert context.response.status_code == 200
    res = json.loads(context.response.data.decode())
    assert res['data']['project']['description'] == description
    assert res['data']['project']['name'] == name


@given(u'a new project was created by the user with title "{title}"')
def step_impl(context, title):
    mutation_vars = {
        'description': "descriptionTest",
        'name': title,
        'goal': 1,
        'deadline': '2022-01-01',
    }
    context.response = context.client.post(
        '/graphql',
        json={
            'query': MUTATION_NEW_PROJECT_SIMPLE,
            'variables': json.dumps(mutation_vars),
        },
        headers={'Authorization': f'Bearer {context.last_token}'},
    )
    context.last_project_id = json.loads(context.response.data.decode())['data'][
        'mutateProject'
    ]['dbId']


@then('the project was cancelled')
def step_impl(context):
    assert context.response.status_code == 200
    res = json.loads(context.response.data.decode())
    assert res['data']['mutateCancelProject']['currentState'] == "CANCELED"
