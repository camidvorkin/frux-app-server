import json

from behave import *  # pylint:disable=wildcard-import,unused-wildcard-import

# pylint:disable=undefined-variable,unused-argument,function-redefined


QUERY_PROJECT_REVIEWS = '''
    query FindProject($dbId: Int!){
        project(dbId: $dbId) {
            generalScore
            reviewCount
            reviews {
                edges {
                    node {
                        projectId
                    }
                }
            }
        }
    }
'''

MUTATION_NEW_REVIEW = '''
    mutation NewReview($idProject: Int!, $score: Float!, $description: String!) {
        mutateReviewProject(idProject: $idProject, score: $score, description: $description) {
            description
        }
    }
'''


@when(u'the project\'s reviews are listed')
def step_impl(context):
    variables = {'dbId': context.last_project_id}
    context.response = context.client.post(
        '/graphql',
        json={'query': QUERY_PROJECT_REVIEWS, 'variables': json.dumps(variables)},
    )


@then(u'the project has {n} reviews and a general score of {score}')
def step_impl(context, n, score):
    assert context.response.status_code == 200

    res = json.loads(context.response.data.decode())
    import pprint

    pprint.pprint(res)
    assert res['data']['project']['generalScore'] == float(score)
    assert len(res['data']['project']['reviews']['edges']) == int(n)
    assert res['data']['project']['reviewCount'] == int(n)


@when(
    u'user "{email}" reviews the project with score {score} and description "{review}"'
)
def step_impl(context, email, score, review):
    variables = {
        'idProject': context.last_project_id,
        'score': float(score),
        'description': review,
    }
    context.response = context.client.post(
        '/graphql',
        json={'query': MUTATION_NEW_REVIEW, 'variables': json.dumps(variables)},
        headers={'Authorization': f'Bearer {email}'},
    )

    assert context.response.status_code == 200
