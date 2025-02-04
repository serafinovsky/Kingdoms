#!/bin/sh
set -e

# Wait for PostgreSQL to be ready
until PGPASSWORD=$POSTGRES_PASSWORD psql -U "$POSTGRES_USER" -c '\q'; do
  echo "PostgreSQL is unavailable - sleeping"
  sleep 1
done

echo "PostgreSQL is up - executing database setup"

# Create user if not exists
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    DO
    \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_user WHERE usename = '$AUTH_PG_USER') THEN
            CREATE USER $AUTH_PG_USER WITH PASSWORD '$AUTH_PG_PASSWORD' CREATEDB;
        END IF;
    END
    \$\$;
EOSQL

# Create database if not exists
if ! psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" -lqt | cut -d \| -f 1 | grep -qw "$AUTH_PG_NAME"; then
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" -c "CREATE DATABASE $AUTH_PG_NAME OWNER $AUTH_PG_USER;"
    echo "Database $AUTH_PG_NAME created"
fi

echo "Database initialization completed"