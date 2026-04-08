# HB-11: Add Client Entity — Operations Requirements

## Definition of Done
The migration script is available so that existing databases might be altered.

## Overview
Existing Happy Bank deployments use a SQLite database (`app.db`) with an `account` table. This change introduces a new `client` table and modifies the `account` table to reference it. The project uses **Alembic** for database migrations (configured in `alembic.ini` with scripts in `migrations/`). An Alembic migration revision must be provided so that existing databases can be upgraded without data loss.

## Migration Script

### Generation

The migration script is generated using Alembic's autogenerate feature after the model changes are implemented:

```bash
alembic revision --autogenerate -m "add client entity"
```

This creates a new revision file in `migrations/versions/`.

### Prerequisites

Ensure that all model modules (including the new `app/models/client.py`) are imported in `migrations/env.py` so that Alembic can detect schema changes. Add the necessary imports:

```python
from app.models.account import Account  # noqa: F401
from app.models.client import Client    # noqa: F401
```

### Expected Migration Content

The auto-generated migration should contain the following operations. Review and adjust the generated script to include data migration logic.

#### Upgrade

1. **Create the `client` table** with columns:
   - `id` (INTEGER, primary key, autoincrement)
   - `name` (TEXT, NOT NULL)
   - `national_number` (TEXT, NOT NULL, UNIQUE)

2. **Add `client_id` column** to the `account` table:
   - `client_id` (INTEGER, foreign key → `client.id`)

3. **Data migration** (must be added manually to the auto-generated script):
   ```python
   op.execute(
       "INSERT INTO client (name, national_number) "
       "VALUES ('Default Client', 'MIGRATION-DEFAULT-0000')"
   )
   op.execute(
       "UPDATE account SET client_id = "
       "(SELECT id FROM client WHERE national_number = 'MIGRATION-DEFAULT-0000')"
   )
   ```

#### Downgrade

1. Remove the `client_id` column from the `account` table.
2. Drop the `client` table.

> **Note:** SQLite has limited `ALTER TABLE` support. Alembic handles this transparently using batch operations when `render_as_batch=True` is set in `context.configure()` in `migrations/env.py`. Verify that this option is enabled if column removal is needed in the downgrade step.

## Execution Instructions

### Applying the Migration

1. **Back up the database** before running the migration:
   ```bash
   cp app.db app.db.backup
   ```

2. **Run the migration**:
   ```bash
   alembic upgrade head
   ```

3. **Verify the migration**:
   ```bash
   sqlite3 app.db ".schema client"
   sqlite3 app.db ".schema account"
   sqlite3 app.db "SELECT COUNT(*) FROM client;"
   sqlite3 app.db "SELECT COUNT(*) FROM account WHERE client_id IS NULL;"
   ```
   - The `client` table should exist with the correct schema.
   - The `account` table should have a `client_id` column.
   - No accounts should have a `NULL` `client_id`.

4. **Check migration status**:
   ```bash
   alembic current
   alembic history
   ```

## Rollback

If the migration needs to be reverted:

```bash
alembic downgrade -1
```

This executes the `downgrade()` function in the migration script, reversing the schema and data changes.

## New Deployments

For **new** deployments (fresh databases), no migration is needed. The application uses `SQLModel.metadata.create_all()` in [`app/main.py`](../../app/main.py), which will create both tables with the correct schema automatically. Default seed data scripts in `resources/data/` should be updated to include default clients and link accounts to them.