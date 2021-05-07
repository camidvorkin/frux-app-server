import json

from behave import *  # pylint:disable=wildcard-import,unused-wildcard-import

# pylint:disable=undefined-variable,unused-argument,function-redefined

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

MUTATION_NEW_PROJECT = '''
    mutation NewProject($description: String!, $userId: Int!, $name: String!, $goal: Int!, $category: String, $hashtags: [String], $state: String) {
        mutateProject(userId: $userId, name: $name, description: $description, goal: $goal, category: $category, state: $state, hashtags: $hashtags) {
            project {
                name,
                description,
                goal,
                category,
                state
            }
        }
    }
'''

variables = {}


@given('a new project')
def step_impl(context):
    pass


@given('project "{name}" has already been created for user {userId}')
@when('user {userId} create a project "{name}"')
def step_impl(context, userId, name):
    variables['userId'] = int(userId)
    variables['name'] = name
    variables['category'] = None
    variables['state'] = None


@given('is about "{description}"')
@when('is about "{description}"')
def step_impl(context, description):
    variables['description'] = description


@given('the category is "{category}"')
@when('the category is "{category}"')
def step_impl(context, category):
    variables['category'] = category


@given('the state is "{state}"')
@when('the state is "{state}"')
def step_impl(context, state):
    variables['state'] = state


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
    )


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
                "project": {
                    "name": str(name),
                    "description": str(description),
                    "goal": int(goal),
                    "category": str(category),
                    "state": str(state),
                }
            }
        }
    }


@then('get a list of {n} projects')
def step_impl(context, n):
    assert context.response.status_code == 200
    res = json.loads(context.response.data.decode())
    assert len(res['data']['allProjects']['edges']) == int(n)
