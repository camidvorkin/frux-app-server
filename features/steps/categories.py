import json

from behave import *  # pylint:disable=wildcard-import,unused-wildcard-import

# pylint:disable=undefined-variable,unused-argument,function-redefined

QUERY_ALL_CATEGORIES = '''
    {
        allCategories {
            edges {
                node {
                    id,
                    name
                }
            }
        }
    }
'''


@when(u'categories are listed')
def step_impl(context):
    context.response = context.client.post(
        '/graphql', json={'query': QUERY_ALL_CATEGORIES}
    )


@then(u'get a list of {n} categories')
def step_impl(context, n):
    res = json.loads(context.response.data.decode())
    assert len(res['data']['allCategories']['edges']) == int(n)
