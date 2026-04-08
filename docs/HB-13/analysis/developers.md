# HB-11: Add Client Entity — Developer Requirements

## Definition of Done
The functionality is properly developed.

## Overview
Introduce a `Client` entity into the Happy Bank application. A client can have multiple accounts, and every account must belong to exactly one client. Two new API endpoints must be provided for listing clients and viewing client details.

## Data Model

### Client Entity
| Field          | Type        | Constraints                        |
|----------------|-------------|------------------------------------|
| `id`           | `int`       | Primary key, auto-generated        |
| `name`         | `str`       | Required, non-empty                |
| `national_number` | `str`   | Required, unique, non-empty        |

### Account Entity (modification)
| Field       | Type    | Constraints                              |
|-------------|---------|------------------------------------------|
| `client_id` | `int`   | Required, foreign key → `client.id`      |

The relationship is **one-to-many**: one `Client` has many `Account`s; each `Account` belongs to exactly one `Client`.

## Implementation Requirements

### 1. Model Layer (`app/models/`)

- **Create `app/models/client.py`** with a `Client` SQLModel class:
  - Fields: `id` (optional, primary key), `name` (str), `national_number` (str, unique).
  - Define a `accounts` relationship to `Account` (one-to-many).
- **Modify `app/models/account.py`**:
  - Add a `client_id: int` foreign key field referencing `client.id`.
  - Add a `client` relationship back-reference to `Client`.

### 2. Repository Layer (`app/repository/`)

- **Create `app/repository/client_repository.py`** with a `ClientRepository` class:
  - `get_all() -> list[Client]` — returns all clients.
  - `get_by_id(client_id: int) -> Client | None` — returns a single client by ID, including their associated accounts.

### 3. Service Layer (`app/services/`)

- **Create `app/services/client_service.py`** with a `ClientService` class:
  - `get_all_clients() -> list[Client]` — delegates to `ClientRepository.get_all()`.
  - `get_client_by_id(client_id: int) -> Client | None` — delegates to `ClientRepository.get_by_id()`.
  - Follow existing logging patterns (see `AccountService` for reference).

### 4. API Layer (`app/api/`)

- **Create `app/api/client_routes.py`** with a FastAPI `APIRouter`:
  - `GET /api/v1/client` — lists all clients (response: list of clients).
  - `GET /api/v1/client/{id}` — returns client details including their accounts. Returns `404` if not found.
- **Modify `app/api/dependencies.py`**:
  - Add a `get_client_service` dependency provider.
- **Modify `app/main.py`**:
  - Register the new `client_routes` router with prefix `/api/v1` and tag `client`.

### 5. Database Migration (`migrations/`)

- After implementing model changes, generate an Alembic migration script:
  ```bash
  alembic revision --autogenerate -m "add client entity"
  ```
- **Important**: Ensure all model modules (including the new `client.py`) are imported in `migrations/env.py` so that Alembic's autogenerate can detect schema changes. Add imports:
  ```python
  from app.models.account import Account  # noqa: F401
  from app.models.client import Client    # noqa: F401
  ```
- Review the auto-generated migration script in `migrations/versions/` and adjust if needed.
- The migration must include data migration logic to seed a default client and link existing accounts to it (see operations requirements for details).
- Test the migration locally:
  ```bash
  alembic upgrade head
  ```

### 6. Startup / Default Data

- **Update `resources/data/`**: Provide a default clients SQL seed script (or update the existing `default_accounts.sql`) so that default accounts are linked to default clients.
- **Update `app/startup.py`**: Ensure default clients are created on first run.

### 7. Constraints & Validation

- The `national_number` field must be enforced as unique at the database level (unique constraint on the column).
- The `client_id` foreign key on `Account` must have a foreign key constraint.
- API responses for client detail should include the list of associated accounts.

### 8. Coding Standards

- Follow existing patterns in the codebase for repository, service, and route structure.
- Include logging as per `.github/instructions/python-log.instructions.md`.
- Code must pass `ruff` linting rules defined in `pyproject.toml`.