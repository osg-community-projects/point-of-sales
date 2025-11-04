# Database Migrations with Alembic

This project uses Alembic for database schema migrations. Alembic provides version control for your database schema.

## Quick Start

### 1. Run Existing Migrations
```bash
# Activate virtual environment
source venv/bin/activate

# Run all pending migrations
alembic upgrade head
```

### 2. Create New Migration
```bash
# After modifying models.py, create a new migration
alembic revision --autogenerate -m "Add new column to products table"

# Review the generated migration file in alembic/versions/
# Then apply the migration
alembic upgrade head
```

## Helper Script

Use the provided `migrate.sh` script for common operations:

```bash
# Create new migration
./migrate.sh create "Add user preferences table"

# Run migrations
./migrate.sh upgrade

# Check current database version
./migrate.sh current

# View migration history
./migrate.sh history

# Downgrade by one revision
./migrate.sh downgrade

# Downgrade to specific revision
./migrate.sh downgrade abc123
```

## Common Commands

### Check Current Database Version
```bash
alembic current
```

### View Migration History
```bash
alembic history --verbose
```

### Create New Migration
```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Create empty migration (for data migrations)
alembic revision -m "Data migration description"
```

### Apply Migrations
```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade abc123

# Apply next migration only
alembic upgrade +1
```

### Rollback Migrations
```bash
# Rollback one migration
alembic downgrade -1

# Rollback to specific revision
alembic downgrade abc123

# Rollback all migrations
alembic downgrade base
```

### View Migration Details
```bash
# Show specific migration
alembic show abc123

# Show current migration
alembic show head
```

## File Structure

```
backend/
├── alembic/                    # Alembic configuration
│   ├── versions/              # Migration files
│   │   └── abc123_description.py
│   ├── env.py                 # Alembic environment
│   └── script.py.mako         # Migration template
├── alembic.ini                # Alembic configuration
└── migrate.sh                 # Helper script
```

## Migration Files

Migration files are stored in `alembic/versions/` and contain:

- **Revision ID**: Unique identifier for the migration
- **Down Revision**: Previous migration in the chain
- **upgrade()**: Function to apply the migration
- **downgrade()**: Function to rollback the migration

Example migration file:
```python
def upgrade() -> None:
    # Create new table
    op.create_table('user_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('theme', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade() -> None:
    # Drop the table
    op.drop_table('user_preferences')
```

## Best Practices

### 1. Always Review Generated Migrations
- Check the generated migration before applying
- Ensure data integrity is maintained
- Add custom logic if needed

### 2. Test Migrations
- Test both upgrade and downgrade functions
- Test with realistic data volumes
- Backup production data before major migrations

### 3. Migration Naming
- Use descriptive names: `add_user_preferences_table`
- Include ticket numbers: `TICKET-123_add_user_preferences`
- Be consistent with naming conventions

### 4. Data Migrations
- Separate schema and data migrations when possible
- Use raw SQL for complex data transformations
- Consider performance for large datasets

### 5. Production Deployments
- Always backup database before migrations
- Test migrations on staging environment first
- Plan for rollback procedures
- Monitor migration performance

## Troubleshooting

### Migration Conflicts
If you get merge conflicts in migration files:
1. Resolve conflicts manually
2. Update revision identifiers
3. Test the migration thoroughly

### Schema Drift
If your database schema doesn't match migrations:
1. Check current database state: `alembic current`
2. Compare with model definitions
3. Create corrective migration if needed

### Failed Migrations
If a migration fails:
1. Check the error message
2. Fix the issue in the migration file
3. Rollback if necessary: `alembic downgrade -1`
4. Re-run the corrected migration

## Environment Configuration

The migration system uses the same database configuration as your application:
- Database URL is read from `app/config.py`
- Environment variables are loaded from `.env`
- Models are imported from `app/models.py`

This ensures consistency between your application and migration system.
