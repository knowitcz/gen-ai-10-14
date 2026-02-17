Happy Bank Frontend — JTBD Analysis

## Job Statement
When practicing and validating banking operations in a training app, I want to quickly switch client context, choose an account or operate across all accounts, view balances and transactions, and execute transfers, so I can learn workflows and verify server interactions without confusion or errors.

## Users & Context
- Primary Persona: Learner/Tester using a training environment to practice banking flows.
- Secondary Persona: Retail client viewing and managing their own accounts.
- Skill Level: Intermediate; comfortable with web apps, needs clear guidance.
- Device: Desktop-first; responsive mobile view is helpful but not critical.
- Accessibility: Keyboard-first navigation, screen reader-friendly labels, clear focus states.

## Current Solution & Pain Points
- Current: Calling API endpoints directly (Swagger/cURL) or minimal HTML mockups.
- Pain:
  - Hard to maintain client context; switching users is cumbersome.
  - Fragmented view of accounts vs transactions; no unified overview.
  - Executing transfers lacks guardrails and inline validation.
  - Filtering transactions by date/account requires manual query building.
- Consequence: Slower learning, frequent mistakes, unclear feedback from the server.

## Desired Outcomes
- Seamless client switcher with instant context updates.
- Clear “All Accounts” vs specific account scopes.
- Unified dashboard summarizing balances and recent activity.
- Guided transaction creation with pre-selected account when applicable.
- Consistent success/error feedback; easy recovery.

## Success Metrics
- Client context switch in < 3 clicks.
- Account selection vs “All Accounts” clearly indicated at all times.
- Transactions discoverable and filterable in < 2 actions.
- Transfer submitted with correct source account in one attempt.
- No abandoned transfers due to unclear errors.