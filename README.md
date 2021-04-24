# frux-app-server
![GitHub tag (latest SemVer)](https://img.shields.io/github/v/tag/camidvorkin/frux-app-server?style=flat-square) ![Coverage](coverage-badge.svg)[![Tests](https://github.com/camidvorkin/frux-app-server/actions/workflows/tests.yml/badge.svg)](https://github.com/camidvorkin/frux-app-server/actions/workflows/tests.yml)[![Linters](https://github.com/camidvorkin/frux-app-server/actions/workflows/linters.yml/badge.svg)](https://github.com/camidvorkin/frux-app-server/actions/workflows/linters.yml)[![Bandit](https://github.com/camidvorkin/frux-app-server/actions/workflows/bandit.yml/badge.svg)](https://github.com/camidvorkin/frux-app-server/actions/workflows/bandit.yml)

Frux app server, for the asignature 'Taller de Programación II, FIUBA'

# Installing the project
This project was built with [poetry](https://python-poetry.org) in mind as the means to manage dependencies. You can follow their [install guide](https://python-poetry.org/docs/#installation) to install it.

Having poetry installed, the following command will install the project into a new environment.

```bash
poetry install
```

Keep in mind that this will by default install the base requirements as well as the dev requirements.

To install the `testing` extras, run:

```bash
poetry install -E testing
```

Remember to commit to the repo the `poetry.lock` file generated by `poetry install`.

# Dev

## Installing pre-commit hooks
We use [pre-commit](https://pre-commit.com) to run several code scans and hooks that make the development cycle easier.
```bash
pre-commit install
pre-commit install -t pre-push
```

## Adding new dependencies
Check the full [poetry](https://python-poetry.org) docs, but here goes a quick reminder,

```bash
poetry add <dependency> [--dev]
```

*Always* remember to commit changes to `poetry.lock`!

## Running nox sessions
In order to bootstrap dependencies and run several actions, we are using [nox](https://nox.thea.codes/en/stable/). This way, dependencies are isolated and you get environment replicability.

To run all sessions,
```bash
poetry run nox
```

To run tests session,
```bash
poetry run nox --sessions tests [-- pylint arguments]
```

To run linting session,
```bash
poetry run nox --sessions cop
```

To run bandit session,
```bash
poetry run nox --sessions bandit
```

To run pyreverse session,
```bash
poetry run nox --sessions pyreverse
```

## Adding new migrations
```bash
poetry run python frux_app_server/manage.py db migrate -m "migration message"
```

Remember to review them after creating them.

## Style guide
frux-app-server follows [PEP8](https://www.python.org/dev/peps/pep-0008/).

If you installed the [pre-commit hooks](#installing-pre-commit-hooks) you shouldn't worry too much about style, since they will fix it for you or warn you about styling errors. We use the following hooks:

- [black](https://github.com/psf/black): An opinionated code formatting tool that ensures consistency across all projects using it
- [flake8](https://github.com/PyCQA/flake8): a tool to enforce style guide
- [mypy](https://github.com/python/mypy): a static type checker for Python
- [pylint](https://github.com/PyCQA/pylint): a source code, bug and quality checker

## Docstrings
We use either [numpy style](https://numpydoc.readthedocs.io/en/latest/format.html) or [google style](https://github.com/google/styleguide/blob/gh-pages/pyguide.md#38-comments-and-docstrings) docstring formatting. It's usually good to include the following docstrings:
- module level docstring giving a general overview of what it does.
- class dosctrings explaining what it is
- method/functions to explain what it does and what it's parameters are

## Testing
We use the [pytest framework](https://docs.pytest.org/en/latest/) to test frux-app-server. The easiest way to run tests it through `nox` with `nox --sessions tests`.

# Docker

Get everything up and running.

```bash
cd docker-compose
docker-compose up --build
```

# Running locally
First make sure you have the db up to date, and then run locally.

```bash
poetry run python frux_app_server/manage.py db upgrade
FLASK_APP=$(pwd)/frux_app_server/app.py poetry run flask run
```

# Deploy to heroku
You will need to have the [heroku cli](https://devcenter.heroku.com/articles/heroku-cli) installed and correctly configured for the following steps.

Prior to the actual deploy, **make sure to commit your changes**.

```bash
heroku create frux-app-server
heroku addons:create heroku-postgresql:hobby-dev
heroku stack:set container
git push heroku master
```

1. The first step [initializes](https://devcenter.heroku.com/articles/creating-apps) a new heroku app
2. The second step provisions a [postgres addon](https://www.heroku.com/postgres)
3. The third step sets the app to use [a docker image](https://devcenter.heroku.com/articles/build-docker-images-heroku-yml). Instead of using a [Procfile](https://devcenter.heroku.com/articles/procfile), we will use a `heroku.yml`. Heroku does not yet support a [poetry buildpack](https://github.com/python-poetry/poetry/issues/403) and exporting a `requirements.txt` from poetry is pretty cumbersome.
4. Deploy 🚀

<!-- ## [Optional] Badge
Add this badge to your readme: `![](https://heroku-badge.herokuapp.com/?app=frux-app-server)` -->

## Diagnosing errors
You can fetch logs from the app using `heroku logs --tail`.

## CD
Go to the app on the [Heroku Dashboard](https://dashboard.heroku.com). On the deploy tab, select "Connect to github" under the "Deployment method" section. Select your repo and you're good to go. Pushes to master will deploy a new version.

## DataDog
The heroku Dockerfile includes the DataDog agent.
Create a new DataDog API Key from [here](https://app.datadoghq.com/account/settings#api).
Remember to set the following config vars:
```bash
heroku config:set DD_API_KEY=<your_api_key>
heroku config:set DD_DYNO_HOST=false
heroku config:set HEROKU_APP_NAME=frux-app-server
heroku config:set DD_TAGS=service:frux_app_server
```

# GitHub Actions
A few pipelines have been set to run on github actions to ensure code quality.

## `sessions.yml`
This workflow runs linters and tests.

# Documentation

## Swagger
You can visit the swagger docs at `127.0.0.1:5000`.
