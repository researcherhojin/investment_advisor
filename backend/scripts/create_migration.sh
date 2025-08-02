#!/bin/bash

# Create Database Migration Script
# Generates a new Alembic migration

set -e

# Check if message is provided
if [ -z "$1" ]; then
    echo "Usage: ./create_migration.sh \"migration message\""
    exit 1
fi

MIGRATION_MESSAGE="$1"

echo "📝 Creating migration: $MIGRATION_MESSAGE"

# Change to backend directory
cd "$(dirname "$0")/.."

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Create migration
alembic revision --autogenerate -m "$MIGRATION_MESSAGE"

echo "✅ Migration created successfully!"
echo ""
echo "To apply the migration, run:"
echo "  alembic upgrade head"