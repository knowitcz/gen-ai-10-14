# Analysis for Developers: Transaction History

## Technical Overview
The goal is to implement a history mechanism for financial operations (deposits, withdrawals) for a client's accounts. Since currently no transaction log exists, we must introduce a new entity and update the existing services to persist this data.

## Database Schema Changes

### New Model: `Transaction`
We need a new table/model called `Transaction`.

| Field Name          | Type               | Description                                                      |
| :---                | :---               | :---                                                             |
| `id`                | `Integer` (PK)     | Unique identifier                                                |
| `source_account_id` | `Integer` (FK)     | Foreign Key to `Account.id`. NULL for deposits (money comes in). |
| `target_account_id` | `Integer` (FK)     | Foreign Key to `Account.id`. NULL for withdrawals (money goes out). |
| `amount`            | `Float/Integer`    | The amount involved                                              |
| `date`              | `DateTime`         | Timestamp of the operation                                       |
| `created_at`        | `DateTime`         | Audit timestamp                                                  |

**Derived transaction type** (not stored, inferred from account ID presence):
- Both `source_account_id` and `target_account_id` set → **TRANSFER**
- Only `source_account_id` set → **WITHDRAWAL**
- Only `target_account_id` set → **DEPOSIT**
- Neither set → **Invalid** (must be prevented by a DB constraint)

### Existing Models
- **Account**: No structural changes, but logic must be updated to create a `Transaction` whenever balance changes (except perhaps initial creation).

## API Specifications

### Endpoint: GET `/clients/{client_id}/transactions`

**Parameters:**
*   `client_id` (path): ID of the client.
*   `from_date` (query, optional): timestamp.
*   `to_date` (query, optional): timestamp.
*   `account_id` (query, optional): Filter by specific account ID belonging to the client.

**Response Body:**
```typescript
interface TransactionResponse {
    summary: {
        total_incoming: number; // Sum of DEPOSITS
        total_outgoing: number; // Sum of WITHDRAWALS
    };
    transactions: Array<{
        id: number;
        source_account_id: number | null;
        target_account_id: number | null;
        amount: number;
        type: string; // Derived: DEPOSIT | WITHDRAWAL | TRANSFER
        date: string;
    }>;
}
```

## Service Layer Logic

1.  **Transaction Creation**:
    - Modify `AccountService` methods `deposit` and `withdraw`.
    - After updating the account balance, create a new `Transaction` record using the same database session (atomic operation).

2.  **Transaction Retrieval**:
    - Create a new method `get_client_transactions(client_id, filters...)` in a new `TransactionService`.
    - Retrieve all accounts for the given `client_id` first.
    - Query `Transaction` table filtering by `source_account_id` or `target_account_id` matching the client's account IDs.
    - Apply date ranges if provided.
    - Compute the summary (total incoming / total outgoing) on the database side using an aggregate query (e.g., `SUM` with `CASE`/`FILTER`), issued as a separate query.
    - Both the transaction list query and the summary aggregation query must run inside the same DB transaction to guarantee they operate on a consistent dataset.

## UML Diagrams

### Class Diagram (Data Structure)

```mermaid
classDiagram
    class Client {
        +int id
        +string name
        +string national_number
    }
    class Account {
        +int id
        +string name
        +float balance
        +string type
        +int client_id
    }
    class Transaction {
        +int id
        +int source_account_id
        +int target_account_id
        +float amount
        +DateTime date
        +type() string
    }

    Client "1" *-- "0..*" Account : owns
    Account "1" *-- "0..*" Transaction : logs (source)
    Account "1" *-- "0..*" Transaction : logs (target)
```

### Sequence Diagram (Data Flow)

**Scenario 1: Viewing History with filters**

```mermaid
sequenceDiagram
    participant API as TransactionController
    participant S as TransactionService
    participant R as TransactionRepository
    participant AR as AccountRepository
    participant DB as Database

    API->>S: get_history(client_id, filters)
    S->>AR: get_accounts_by_client(client_id)
    AR->>DB: SELECT * FROM accounts WHERE client_id = ?
    DB-->>AR: [Account1, Account2]
    AR-->>S: [Account1, Account2]

    Note right of S: Extract List<account_id>

    Note right of S: Begin DB transaction

    S->>R: find_transactions(account_ids, dates)
    R->>DB: SELECT * FROM transactions WHERE (source_account_id IN (...) OR target_account_id IN (...)) AND date BETWEEN ...
    DB-->>R: [Tx1, Tx2, Tx3]
    R-->>S: [Tx1, Tx2, Tx3]

    S->>R: get_summary(account_ids, dates)
    R->>DB: SELECT SUM(CASE ...) AS total_incoming, SUM(CASE ...) AS total_outgoing FROM transactions WHERE ...
    DB-->>R: {total_incoming, total_outgoing}
    R-->>S: Summary

    Note right of S: End DB transaction

    S-->>API: Response(summary, list)
```

**Scenario 2: Creating a Transaction (Deposit)**

```mermaid
sequenceDiagram
    participant API as AccountController
    participant S as AccountService
    participant R as AccountRepository
    participant DB as Database

    API->>S: deposit(account_id, amount)
    S->>R: get_account(id)
    R-->>S: Account check

    S->>S: account.balance += amount
    S->>R: update_account(account)

    Note right of S: New step: Log transaction
    S->>R: create_transaction(source_account_id=None, target_account_id=account_id, amount)

    R->>DB: UPDATE account... INSERT INTO transaction...
    DB-->>R: Success
    R-->>S: Success
    S-->>API: Success
```
