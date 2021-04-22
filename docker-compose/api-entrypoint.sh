#!/bin/bash
docker-compose/wait-for-postgres.sh

echo 'creating db'
poetry run python frux_app_server/manage.py db_create
echo 'upgrading db'
poetry run python frux_app_server/manage.py db upgrade
echo 'starting server'
poetry run gunicorn -w 2 --bind 0.0.0.0:5000 "frux_app_server.app:create_app()"
