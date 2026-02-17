# Analysis for Testers: Transaction History

## Functionality Description
The goal is to allow users to view a history of financial operations (transactions) for a specific client. This includes both withdrawals and deposits across **all** accounts owned by the client.

To refine the results, the user can optionally filter by:
*   **From Date**: Show transactions starting from this date.
*   **To Date**: Show transactions up to this date.
*   **Account**: Show transactions only for a specific account belonging to the client.

The response will include:
1.  **List of Transactions**: Details of each operation (amount, type, date, account).
2.  **Summary**:
    *   **Total Incoming**: Sum of all deposit operations in the filtered set.
    *   **Total Outgoing**: Sum of all withdrawal operations in the filtered set.

## Test Data Strategy
To properly test the "all accounts" requirement, the default data must be updated so that at least one client has multiple accounts.

**Current Setup:**
*   Alice: 1 Account
*   Bob: 1 Account

**Required Setup:**
*   **Alice**:
    *   Account 1 (checking)
    *   Account 2 (savings) - **NEW**
*   **Bob**: 1 Account

## API Response Structure (Draft)

```json
{
  "summary": {
    "total_incoming": 1500.00,
    "total_outgoing": 200.00
  },
  "transactions": [
    {
      "id": 1,
      "account_id": 1,
      "type": "DEPOSIT",
      "amount": 1000.00,
      "date": "2023-10-01T10:00:00"
    },
    {
      "id": 2,
      "account_id": 2,
      "type": "DEPOSIT",
      "amount": 500.00,
      "date": "2023-10-02T11:00:00"
    },
    {
      "id": 3,
      "account_id": 1,
      "type": "WITHDRAWAL",
      "amount": 200.00,
      "date": "2023-10-05T09:30:00"
    }
  ]
}
```

## Gherkin Test Scenarios

### Feature: Client Transaction History

```gherkin
  Background:
    Given the following clients exist:
      | name  | national_number |
      | Alice | 123456/7890     |
    And the following accounts exist for "Alice":
      | name        | type | initial_balance |
      | Alice Main  | CASH | 1000            |
      | Alice Saver | CASH | 500             |
    And the following transactions have occurred:
      | account_name | type       | amount | date       |
      | Alice Main   | DEPOSIT    | 1000   | 2023-01-01 |
      | Alice Saver  | DEPOSIT    | 500    | 2023-01-02 |
      | Alice Main   | WITHDRAWAL | 100    | 2023-01-10 |
      | Alice Main   | WITHDRAWAL | 50     | 2023-02-01 |

  Scenario: View all transactions for a client (no filters)
    When I request the transaction history for client "Alice"
    Then the response should contain 4 transactions
    And the summary "total_incoming" should be 1500
    And the summary "total_outgoing" should be 150

  Scenario: Filter transactions by date range
    When I request the transaction history for client "Alice"
    And I apply the filter "from_date" as "2023-01-05"
    And I apply the filter "to_date" as "2023-01-31"
    Then the response should contain 1 transaction
    And the transaction should be the "WITHDRAWAL" of 100 on "2023-01-10"
    And the summary "total_incoming" should be 0
    And the summary "total_outgoing" should be 100

  Scenario: Filter transactions by specific account
    When I request the transaction history for client "Alice"
    And I apply the filter "account_id" corresponding to "Alice Saver"
    Then the response should contain 1 transaction
    And the summary "total_incoming" should be 500
    And the summary "total_outgoing" should be 0

  Scenario: Client with no transactions
    Given the client "Bob" exists with 1 account
    And no transactions have occurred for "Bob"
    When I request the transaction history for client "Bob"
    Then the response should contain 0 transactions
    And the summary "total_incoming" should be 0
    And the summary "total_outgoing" should be 0
```