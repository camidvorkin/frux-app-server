import json

from behave import *  # pylint:disable=wildcard-import,unused-wildcard-import

# pylint:disable=undefined-variable,unused-argument,function-redefined

QUERY_STATS = '''
    {
        stats {
            totalUsers,
            totalSeers,
            totalProjects,
            totalFavorites,
            totalHashtags,
            totalInvestments
        }
    }
'''


@when(u'the stats are listed')
def step_impl(context):
    context.response = context.client.post('/graphql', json={'query': QUERY_STATS},)


@then(u'the total users should be {n}')
def step_impl(context, n):
    res = json.loads(context.response.data.decode())
    assert res['data']['stats']['totalUsers'] == int(n)


@then(u'the total seers should be {n}')
def step_impl(context, n):
    res = json.loads(context.response.data.decode())
    assert res['data']['stats']['totalSeers'] == int(n)


@then(u'the total projects should be {n}')
def step_impl(context, n):
    res = json.loads(context.response.data.decode())
    assert res['data']['stats']['totalProjects'] == int(n)


@then(u'the total favorites should be {n}')
def step_impl(context, n):
    res = json.loads(context.response.data.decode())
    assert res['data']['stats']['totalFavorites'] == int(n)


@then(u'the total investments should be {n}')
def step_impl(context, n):
    res = json.loads(context.response.data.decode())
    assert res['data']['stats']['totalInvestments'] == int(n)


@then(u'the total hashtags should be {n}')
def step_impl(context, n):
    res = json.loads(context.response.data.decode())
    assert res['data']['stats']['totalHashtags'] == int(n)
