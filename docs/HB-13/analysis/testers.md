# HB-11: Add Client Entity — Tester Requirements

## Definition of Done
The functionality is properly tested by automated tests.

## Overview
Automated tests must be written to verify the new Client entity, its relationship with Account, the repository, service, and API layers. Tests should follow the existing conventions: `pytest` framework, `unittest.mock` for mocking, and test doubles where appropriate.

## Test Scope

### 1. Repository Tests (`app/repository/test_client_repository.py`)

| Test Case | Description |
|-----------|-------------|
| `test_get_all_returns_empty_list` | When no clients exist, `get_all()` returns an empty list. |
| `test_get_all_returns_all_clients` | When multiple clients exist, `get_all()` returns all of them. |
| `test_get_by_id_returns_client` | When a client exists, `get_by_id()` returns the correct client. |
| `test_get_by_id_returns_none` | When a client does not exist, `get_by_id()` returns `None`. |
| `test_get_by_id_includes_accounts` | When a client has accounts, `get_by_id()` returns the client with their associated accounts. |
| `test_get_by_id_client_with_no_accounts` | When a client has no accounts, the accounts list is empty. |

### 2. Service Tests (`app/services/test_client_service.py`)

| Test Case | Description |
|-----------|-------------|
| `test_get_all_clients_delegates_to_repository` | `get_all_clients()` calls `ClientRepository.get_all()` and returns its result. |
| `test_get_all_clients_returns_empty_list` | When repository returns empty list, service returns empty list. |
| `test_get_client_by_id_returns_client` | `get_client_by_id()` calls `ClientRepository.get_by_id()` and returns the client. |
| `test_get_client_by_id_returns_none` | When repository returns `None`, service returns `None`. |

Use `unittest.mock.Mock` to mock the `ClientRepository`, consistent with existing tests in `test_account_service.py`.

### 3. Model / Relationship Tests

| Test Case | Description |
|-----------|-------------|
| `test_client_has_required_fields` | `Client` model has `id`, `name`, and `national_number` fields. |
| `test_account_has_client_id_field` | `Account` model has a `client_id` field. |
| `test_national_number_uniqueness` | Attempting to create two clients with the same `national_number` raises an integrity error (this may be tested at the repository or integration level). |

### 4. API / Route Tests (optional but recommended)

If integration or endpoint tests are added:

| Test Case | Description |
|-----------|-------------|
| `test_get_clients_endpoint_returns_200` | `GET /api/v1/client` returns HTTP 200 with a list. |
| `test_get_client_by_id_endpoint_returns_200` | `GET /api/v1/client/{id}` returns HTTP 200 for an existing client. |
| `test_get_client_by_id_endpoint_returns_404` | `GET /api/v1/client/{id}` returns HTTP 404 for a non-existing client. |
| `test_get_client_by_id_includes_accounts` | The detail response includes the client's accounts. |

### 5. Existing Test Maintenance

- **Verify existing tests still pass** after the `Account` model is modified to include `client_id`. Update test doubles (e.g., `DummyAccount` in `test_account_repository.py` and `test_account_service.py`) to include the new `client_id` field if necessary.
- Ensure no regressions in `test_account_repository.py`, `test_account_service.py`, `test_bank_service.py`, and `test_amount_validator.py`.

### 6. Test Conventions

- Place test files alongside the code they test (e.g., `app/repository/test_client_repository.py`, `app/services/test_client_service.py`).
- Use descriptive test names following the `test_<what>_<expected_behavior>` pattern.
- Use `pytest.raises` for expected exceptions.
- Use `Mock` and `MagicMock` from `unittest.mock` for isolation.
- All tests must be runnable via `uv run pytest app/ -v --tb=short`.