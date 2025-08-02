#!/bin/bash

# Initialize Database Script
# Sets up PostgreSQL database and runs initial migrations

set -e

echo "🗄️  Initializing Database..."
echo "=========================="

# Database configuration
DB_USER="${DB_USER:-stock_user}"
DB_PASSWORD="${DB_PASSWORD:-stock_dev_password}"
DB_NAME="${DB_NAME:-stock_db}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

# Check if PostgreSQL is running
if ! pg_isready -h $DB_HOST -p $DB_PORT > /dev/null 2>&1; then
    echo "❌ PostgreSQL is not running on $DB_HOST:$DB_PORT"
    exit 1
fi

echo "✅ PostgreSQL is running"

# Create user if it doesn't exist
echo "Creating database user..."
psql -h $DB_HOST -p $DB_PORT -U postgres <<EOF 2>/dev/null || true
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
EOF

# Create database if it doesn't exist
echo "Creating database..."
createdb -h $DB_HOST -p $DB_PORT -U postgres -O $DB_USER $DB_NAME 2>/dev/null || echo "Database $DB_NAME already exists"

# Grant privileges
echo "Granting privileges..."
psql -h $DB_HOST -p $DB_PORT -U postgres <<EOF
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF

# Change to backend directory
cd "$(dirname "$0")/.."

# Set environment variables
export DATABASE_URL="postgresql+asyncpg://$DB_USER:$DB_PASSWORD@$DB_HOST:$DB_PORT/$DB_NAME"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Create initial migration if none exists
if [ ! -d "alembic/versions" ] || [ -z "$(ls -A alembic/versions 2>/dev/null)" ]; then
    echo "Creating initial migration..."
    alembic revision --autogenerate -m "Initial schema"
fi

# Run migrations
echo "Running migrations..."
alembic upgrade head

echo ""
echo "✅ Database initialization complete!"
echo ""
echo "Database URL: $DATABASE_URL"