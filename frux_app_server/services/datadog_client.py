import os

from datadog import initialize
from datadog.threadstats import ThreadStats

statsd = ThreadStats()
statsd.start()

ENVIRON = f"frux-app-server:{os.environ.get('ENVIRONMENT', 'test')}"


def start():
    options = {'statsd_host': '127.0.0.1', 'statsd_port': 8125}

    initialize(**options)


def new_login(provider):
    statsd.increment(f'frux-app-server.new-login.{provider}', tags=[ENVIRON])


def new_user(provider):
    statsd.increment(f'frux-app-server.new-user.{provider}', tags=[ENVIRON])


def new_blocked_user():
    statsd.increment('frux-app-server.new-blocked-user', tags=[ENVIRON])


def new_unblocked_user():
    statsd.increment('frux-app-server.new-blocked-user', tags=[ENVIRON])
