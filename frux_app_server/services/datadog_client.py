import os

from datadog import initialize
from datadog.threadstats import ThreadStats

from frux_app_server.graphqlschema.constants import states
from frux_app_server.models import Category, Project, User, db

statsd = ThreadStats()

ENVIRON = f"frux-app-server:{os.environ.get('ENVIRONMENT', 'test')}"


def update_users():
    statsd.gauge(
        'frux-app-server.total-users', db.session.query(User).count(), tags=[ENVIRON],
    )


def new_login(provider):
    statsd.increment(f'frux-app-server.new-login.{provider}', tags=[ENVIRON])


def new_user(provider):
    statsd.increment(f'frux-app-server.new-user.{provider}', tags=[ENVIRON])
    update_users()


def update_blocked_users():
    statsd.gauge(
        'frux-app-server.blocked-users',
        db.session.query(User).filter(User.is_blocked).count(),
        tags=[ENVIRON],
    )


def new_blocked_user():
    update_blocked_users()


def new_unblocked_user():
    update_blocked_users()


def set_project_in_category(category, n=None):
    if n is None:
        n = db.session.query(Project).filter(Project.category_name == category).count()
    statsd.gauge(
        'frux-app-server.project.category', n, tags=[ENVIRON, f'category:{category}']
    )


def set_project_in_state(state, n=None):
    if n is None:
        n = db.session.query(Project).filter(Project.current_state == state).count()
    statsd.gauge(
        'frux-app-server.project.current_state', n, tags=[ENVIRON, f'state:{state}']
    )


def refresh_categories():
    categories = db.session.query(Category).all()
    for category in categories:
        set_project_in_category(category.name)


def refresh_states():
    for state in states:
        set_project_in_state(state)


def start(new_app):
    options = {'statsd_host': '127.0.0.1', 'statsd_port': 8125}
    initialize(**options)
    statsd.start()

    if os.environ.get('ENVIRONMENT', 'test') == 'test':
        return

    with new_app.app_context():
        refresh_categories()
        refresh_states()
        update_blocked_users()
        update_users()
