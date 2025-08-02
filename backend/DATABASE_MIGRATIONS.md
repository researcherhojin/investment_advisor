# Database Migrations Guide

## Overview

This project uses Alembic for database schema migrations with async SQLAlchemy support.

## Initial Setup

### 1. Install PostgreSQL

```bash
# macOS
brew install postgresql
brew services start postgresql

# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### 2. Initialize Database

Run the initialization script:

```bash
cd backend
./scripts/init_db.sh
```

This will:
- Create database user `stock_user`
- Create database `stock_db`
- Grant necessary privileges
- Create initial migration
- Run all migrations

### 3. Environment Variables

Set the following in your `.env` file:

```env
DATABASE_URL=postgresql+asyncpg://stock_user:stock_dev_password@localhost:5432/stock_db
```

## Working with Migrations

### Creating a New Migration

1. **Automatic Migration** (recommended):
   ```bash
   ./scripts/create_migration.sh "Add new feature tables"
   ```
   This auto-generates migration based on model changes.

2. **Manual Migration**:
   ```bash
   alembic revision -m "Custom migration"
   ```
   Then edit the generated file in `alembic/versions/`.

### Applying Migrations

```bash
# Apply all migrations
alembic upgrade head

# Apply next migration
alembic upgrade +1

# Apply to specific revision
alembic upgrade <revision_id>
```

### Rolling Back Migrations

```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade <revision_id>

# Rollback all migrations
alembic downgrade base
```

### Checking Migration Status

```bash
# Show current revision
alembic current

# Show migration history
alembic history

# Show migration history with details
alembic history --verbose
```

## Migration Best Practices

### 1. Always Review Auto-generated Migrations

Auto-generated migrations may not be perfect. Always review:
- Index creation
- Foreign key constraints
- Default values
- Data type changes

### 2. Test Migrations

```bash
# Test upgrade
alembic upgrade head

# Test downgrade
alembic downgrade -1

# Test upgrade again
alembic upgrade head
```

### 3. Handle Data Migrations Carefully

For data migrations:
```python
def upgrade():
    # Create new column with nullable=True
    op.add_column('users', sa.Column('new_field', sa.String(), nullable=True))
    
    # Populate data
    connection = op.get_bind()
    result = connection.execute('UPDATE users SET new_field = ...')
    
    # Make column non-nullable if needed
    op.alter_column('users', 'new_field', nullable=False)
```

### 4. Backup Before Major Migrations

```bash
# Backup database
pg_dump -U stock_user stock_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Run migration
alembic upgrade head

# If something goes wrong, restore
psql -U stock_user stock_db < backup_20240115_143022.sql
```

## Common Issues

### 1. Import Errors

**Problem**: `ModuleNotFoundError` when running migrations

**Solution**: Set PYTHONPATH
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
alembic upgrade head
```

### 2. Async Engine Issues

**Problem**: `AttributeError: 'AsyncEngine' object has no attribute 'execute'`

**Solution**: Ensure `env.py` uses `run_sync()` for migrations

### 3. Duplicate Migration

**Problem**: Migration conflicts after merge

**Solution**:
```bash
# Check current state
alembic current

# Manually resolve by editing alembic_version table
psql -U stock_user stock_db
UPDATE alembic_version SET version_num = '<correct_revision>';
```

### 4. Failed Migration

**Problem**: Migration fails halfway

**Solution**:
1. Check error message
2. Fix the issue in migration file
3. If partially applied, manually rollback changes
4. Re-run migration

## Production Migrations

### 1. Pre-deployment Checklist

- [ ] Test migration on staging environment
- [ ] Backup production database
- [ ] Review migration for performance impact
- [ ] Plan for rollback scenario
- [ ] Schedule during low-traffic period

### 2. Running Production Migrations

```bash
# Set production database URL
export DATABASE_URL=$PRODUCTION_DATABASE_URL

# Dry run (shows SQL without executing)
alembic upgrade head --sql

# Apply migration
alembic upgrade head

# Verify
alembic current
```

### 3. Zero-downtime Migrations

For zero-downtime deployments:

1. **Add nullable columns**
   ```python
   op.add_column('table', sa.Column('new_col', sa.String(), nullable=True))
   ```

2. **Deploy new code that handles both schemas**

3. **Backfill data**
   ```python
   op.execute("UPDATE table SET new_col = old_col")
   ```

4. **Make column non-nullable**
   ```python
   op.alter_column('table', 'new_col', nullable=False)
   ```

5. **Remove old column in next release**

## Schema Documentation

Current schema includes:

- **users**: User accounts
- **stocks**: Stock information
- **analysis_sessions**: Analysis workflow tracking
- **agent_analyses**: Individual agent results
- **investment_decisions**: Final investment recommendations
- **price_history**: Historical price data
- **watchlists**: User watchlists

See `infrastructure/database/models.py` for complete schema definition.