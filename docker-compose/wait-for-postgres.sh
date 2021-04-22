#!/bin/sh
# wait-for-postgres.sh

# Based on https://docs.docker.com/compose/startup-order/

set -e

host=$(python -c "import os; print(os.getenv('DATABASE_URL').rsplit('/', 1)[0])")

until psql -d $host -c '\q'; do
    >&2 echo "Postgres is unavailable - sleeping for 5s"
    sleep 5
done

echo "Postgres is up"

