Happy Bank Frontend — User Journey

## User Persona
- Who: Learner/Tester practicing banking flows in a training app.
- Goal: Switch between clients, manage accounts, view transactions, and make transfers.
- Context: Focused desktop sessions; repeating tasks to understand server interactions.
- Success Metric: Complete a transfer and verify transaction history within 5 minutes.

## Journey Stages

### Stage 1: Awareness — Pick Client
**Doing**: Opening app, locating client switcher.
**Thinking**: "Which client should I use? Will the context apply everywhere?"
**Feeling**: Curious but cautious.
**Pain Points**:
- Client context isn’t clearly visible across screens.
- Switching resets filters unexpectedly.
**Opportunity**: Persistent client context indicator; non-destructive context switches.

### Stage 2: Exploration — Choose Account Scope
**Doing**: Selecting a specific account or choosing “All Accounts”.
**Thinking**: "I need to see a balance now, or a full overview."
**Feeling**: Seeking clarity.
**Pain Points**:
- Ambiguous scope; unclear which transactions will show.
- Hard to find balances across accounts.
**Opportunity**: Scope chips (All Accounts vs Account X) and clear balance cards.

### Stage 3: Action — Review Balances & Transactions
**Doing**: Viewing current balance/cards; opening transactions table; filtering by date/account.
**Thinking**: "Did the last transfer post? Are filters applied correctly?"
**Feeling**: Analytical; wants verification.
**Pain Points**:
- Filters not persistent when navigating.
- No quick way to jump from account to related transactions.
**Opportunity**: Linked cards to filtered transactions; saved filters per client.

### Stage 4: Transfer — Execute Transaction
**Doing**: Opening transfer form; source account pre-selected when in Account scope; choosing source in All Accounts; submitting.
**Thinking**: "Is the amount valid? Will I get a confirmation?"
**Feeling**: Slight anxiety; needs reassurance.
**Pain Points**:
- Missing inline validation and clear error messages.
- Confusing source/destination selection in All Accounts mode.
**Opportunity**: Guided form with validation, defaults from context, clear success toast and redirect.

### Stage 5: Outcome — Confirm & Verify
**Doing**: Viewing success message; returning to transactions to verify entry; optionally exporting.
**Thinking**: "I can see it posted and balances updated."
**Feeling**: Confident.
**Success Metrics**:
- Balance and transactions refresh automatically post-transfer.
- Clear visual confirmation; easy to repeat actions.