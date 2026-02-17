Happy Bank Frontend — Flow Specification

## Entry Point
- App loads with most recent or default client context.
- Visible client context badge with quick switcher control in header.

## Flow Steps
1. Client Switcher (Header Dropdown / Modal)
   - Lists clients from GET /client.
   - Selecting a client sets global context; updates views without page reload.
   - Shows key details from GET /client/{id} (name, client id).

2. Dashboard (All Accounts Scope)
   - Scope control: “All Accounts” chip vs per-account chips.
   - Account list with balance cards (account name, id, current balance).
   - Recent transactions summary across all accounts (top N rows).

3. Account Detail View (Specific Account Scope)
   - Header shows selected account with balance from GET /account/{id}.
   - Quick actions: “Transfer” (primary), optional “Withdraw”.
   - Link to Transactions auto-filters by this account.

4. Transactions View
   - Data source: GET /clients/{client_id}/transactions with optional filters:
     - from_date, to_date (date pickers)
     - account_id (auto-set in Account scope; selectable in All Accounts)
   - Table: date, amount (+/-), description, source/destination, account.
   - Controls: filter panel, clear filters, export CSV.

5. Transfer Flow (Modal/Drawer)
   - Source account:
     - Pre-selected when in Account scope.
     - Selectable from user’s accounts in All Accounts scope.
   - Destination account: searchable input (could be within bank).
   - Amount: numeric with inline validation (min > 0, sufficient funds).
   - Submit triggers POST /bank/transfer.
   - Success: toast + auto-refresh of balance and transactions.
   - Error: inline message with recovery guidance.

6. Withdraw Flow (Optional)
   - Source is selected account or chosen from list.
   - Submit triggers POST /account/withdraw.
   - Same success/error handling as Transfer.

## API Integration Mapping
- List Clients: GET /client → client switcher options.
- Client Details: GET /client/{id} → context badge details.
- Account Detail: GET /account/{id} → account header and balance.
- Transactions: GET /clients/{client_id}/transactions?from_date&to_date&account_id → table.
- Transfer: POST /bank/transfer → transfer modal submission.
- Withdraw: POST /account/withdraw → optional quick action.

## Components Inventory
- Header: logo, client switcher, context badge.
- Scope Selector: chips for “All Accounts” + per-account.
- Account Card: name, id, balance, link to transactions.
- Transactions Table: sortable columns, filter panel, empty state.
- Transfer Modal: form fields, validation, submit/cancel.
- Toast/Alerts: success, error, info.

## Design Principles
- Progressive Disclosure: emphasize scope; reveal advanced filters on demand.
- Clear Context: persistent client and scope indicators; no hidden state.
- Guided Actions: defaults from context; minimize choices where possible.
- Immediate Feedback: toasts and auto-refresh after operations.
- Consistency: same patterns for account-scoped vs all-account views.

## Accessibility Requirements
- Keyboard Navigation: Tab order through header, scope chips, tables, and modals; Enter/Space activate buttons; Escape closes modals.
- Screen Reader: Labels for inputs, descriptive alt text, ARIA live regions for toasts and table updates.
- Visual: High contrast for scope chips and table; visible focus indicators; touch targets ≥ 44px where applicable.
- Error Announcements: Validation errors announced; error text not color-only.

## States & Recovery
- Empty States: No transactions → friendly message and link to make a transfer.
- Loading States: Skeletons for cards and table; spinner in modal submit.
- Error States: Inline messages with retry; preserve user inputs.

## Information Architecture (Desktop)
- Layout: Header (top), Scope & Account cards (left/main), Transactions (main), Actions (right or modal).
- Navigation: Dashboard ↔ Account detail ↔ Transactions linked via scope.