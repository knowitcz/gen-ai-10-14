# Analysis for Developers: Transaction History

## Technical Overview
The goal is to implement a history mechanism for financial operations (deposits, withdrawals) for a client's accounts. Since currently no transaction log exists, we must introduce a new entity and update the existing services to persist this data.

## Database Schema Changes

### New Model: `Transaction`
We need a new table/model called `Transaction`.

| Field Name   | Type               | Description                                  |
| :---         | :---               | :---                                         |
| `id`         | `Integer` (PK)     | Unique identifier                            |
| `account_id` | `Integer` (FK)     | Foreign Key to `Account.id`                  |
| `type`       | `Enum/String`      | 'DEPOSIT', 'WITHDRAWAL', 'TRANSFER' (future) |
| `amount`     | `Float/Integer`    | The amount involved                          |
| `date`       | `DateTime`         | Timestamp of the operation                   |
| `created_at` | `DateTime`         | Audit timestamp                              |

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
        account_id: number;
        amount: number;
        type: string;
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
    - Query `Transaction` table filtering by the list of account IDs.
    - Apply date ranges if provided.
    - Calculate sums for incoming vs outgoing.

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
        +int account_id
        +string type
        +float amount
        +DateTime date
    }

    Client "1" *-- "0..*" Account : owns
    Account "1" *-- "0..*" Transaction : logs
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

    S->>R: find_transactions(account_ids, dates)
    R->>DB: SELECT * FROM transactions WHERE account_id IN (...) AND date BETWEEN ...
    DB-->>R: [Tx1, Tx2, Tx3]
    R-->>S: [Tx1, Tx2, Tx3]

    S->>S: calculate_summary(transactions)
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
    S->>R: create_transaction(account_id, amount, 'DEPOSIT')

    R->>DB: UPDATE account... INSERT INTO transaction...
    DB-->>R: Success
    R-->>S: Success
    S-->>API: Success
```
