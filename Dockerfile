FROM python:3.7.7-stretch
RUN apt-get update && apt-get install -y postgresql-client
RUN pip install poetry
WORKDIR /app
ENV POETRY_VIRTUALENVS_IN_PROJECT true
COPY . .
RUN poetry install
RUN poetry run pip install gunicorn
