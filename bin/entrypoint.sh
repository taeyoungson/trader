#!/bin/sh

MYSQL_HOST="db"
MYSQL_PORT="${MYSQL_PORT:-3306}"

echo "Waiting for database at ${MYSQL_HOST}:${MYSQL_PORT}..."

while ! nc -zv ${MYSQL_HOST} ${MYSQL_PORT}; do
  echo "Database is unavailable - sleeping"
  sleep 1
done

echo "Database started"
echo "Running database migrations..."

uv run alembic upgrade head

exec "$@"
