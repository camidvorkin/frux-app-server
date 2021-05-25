import json

from behave import *  # pylint:disable=wildcard-import,unused-wildcard-import

from frux_app_server.models import Admin

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
    mutation NewProject($description: String!, $name: String!, $goal: Int!, $category: String, $hashtags: [String], $stage: String) {
        mutateProject(name: $name, description: $description, goal: $goal, category: $category, stage: $stage, hashtags: $hashtags) {
            project {
                name,
                description,
                goal,
                category,
                stage {
                    stage
                }
            }
        }
    }
'''

variables = {}


@given('a new project')
def step_impl(context):
    pass


@given('user with mail "{email}" is authenticated')
def step_impl(context, email):
    admin = Admin(email=email, token=ADMIN_TOKEN)
    with context.app.app_context():
        context.db.session.add(admin)
        context.db.session.commit()


@given('project "{name}" has already been created for user')
@when('user create a project "{name}"')
def step_impl(context, name):
    variables['name'] = name
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
        headers={'Authorization': f'Bearer {ADMIN_TOKEN}'},
    )


@when('projects are listed')
def step_impl(context):
    context.response = context.client.post(
        '/graphql', json={'query': QUERY_ALL_PROJECT}
    )


@then(
    'the project "{name}", description "{description}", category "{category}", stage "{stage}" and goal {goal} is created correctly'
)
def step_impl(context, name, description, goal, category, stage):
    res = json.loads(context.response.data.decode())
    import pprint

    pprint.pprint(res)
    assert res == {
        "data": {
            "mutateProject": {
                "project": {
                    "name": str(name),
                    "description": str(description),
                    "goal": int(goal),
                    "category": str(category),
                    "stage": {"stage": str(stage)},
                }
            }
        }
    }


@then('get a list of {n} projects')
def step_impl(context, n):
    assert context.response.status_code == 200
    res = json.loads(context.response.data.decode())
    assert len(res['data']['allProjects']['edges']) == int(n)


@when(u'projects are listed filtering by name "{name}"')
def step_impl(context, name):
    context.response = context.client.post(
        '/graphql',
        json={
            'query': QUERY_ALL_PROJECT_FILTERS,
            'variables': json.dumps({'name': name}),
        },
    )
