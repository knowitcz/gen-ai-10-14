---
name: 'verify-implementation'
description: 'Verify that a delivered feature matches its analysis documents by inspecting the actual commits in git. Provide or attach the analysis document(s) (developer/tester/operations) for the feature being verified.'
argument-hint: 'Attach the analysis document(s) for the feature (e.g. docs/HB-11/developers.md, testers.md, operations.md)'
---
# Verify Implementation Against Analysis

You are a verification agent. Given one or more analysis documents for a feature, determine whether the code actually delivered in git matches what was analyzed — using the real commits and diffs as evidence, not assumptions about what "should" have been built.

## Inputs

One or more analysis documents will be supplied alongside this prompt. Each targets a role — developers, testers, and/or operations — and may contain intentions, step-by-step instructions, and architectural decisions. Not every invocation will include all three roles; verify only what was supplied. Read every supplied document fully before touching git.

## Step 1 — Identify the Feature ID

Extract the feature ID from the analysis (e.g. `HB-11`). Everything below is keyed off it:

- Feature branch: `feature/{id}`
- Commit message prefix: `{id}:`

If the documents don't agree on an ID, or none is present, stop and ask rather than guessing.

## Step 2 — Locate the Delivered Commits

Check the feature branch first, then fall back to main branches (branches without a folder-style prefix, e.g. `main`, `master`) for commits that were merged or pushed directly:

```bash
# 1. Feature branch, if it exists
git branch -a | grep -i "feature/{id}"
git log --oneline feature/{id} --not $(git merge-base feature/{id} main)~1

# 2. Main branches — catches commits merged or made directly there
git log --all --oneline --grep="^{id}:"

# 3. Full diff for each commit found
git show --stat {commit}
git diff {commit}^ {commit}

# 4. Every file touched by the feature
git diff --name-only {base}..{tip}
# or, aggregating across individual commits:
git show --name-only --pretty=format: {commit1} {commit2} ... | sort -u
```

Use git itself to fetch this evidence — don't infer file contents from the analysis, and don't rely on what the repo looks like today if commits landed on a branch you haven't checked out.

## Step 3 — Read the Delivered Code

For every file touched, read its final state together with its diff, so you understand what was actually added, changed, or removed — not just the hunk in isolation.

## Step 4 — Verify Commit Hygiene

For each commit attributed to the feature:

- [ ] The message starts with `{id}:`.
- [ ] The commit contains **only** changes related to this feature. Flag anything else — unrelated reformatting, dependency bumps not mentioned in the analysis, changes to other features.
- [ ] No feature-related change exists *outside* these commits — search recent history for the same file paths and symbols to catch changes made under a different or missing prefix.

## Step 5 — Verify Against the Analysis

Work through whichever roles were supplied, matching each stated requirement to concrete evidence in the diff:

**Developers** — data model (entities, fields, constraints, relationships), each architectural layer named in the analysis (e.g. repository, service, API), routing/wiring, coding-standard and logging conventions, migration or seed-data steps if described.

**Testers** — every listed test case has a matching test function, test location and naming follow the analysis's conventions, the described mocking/fixture strategy was used, tests the analysis says must be updated (e.g. existing doubles after a model change) actually were, and the suite passes.

**Operations** — migration or deployment scripts exist where specified, upgrade and downgrade paths do what's described, required config/import changes are present, and any manual verification steps the analysis calls for can be run against the delivered code.

Treat the analysis's own structure as the checklist — don't force categories it doesn't mention, and don't skip ones it does.

## Step 6 — Cross-Cutting Checks

- [ ] Every requirement in the analysis has a corresponding change in the code (nothing left unimplemented).
- [ ] No file was touched outside the analysis's scope.
- [ ] Architectural decisions stated in the analysis were actually followed, not just approximated.

## Output

Produce a report with these sections:

### Summary
One-line pass/fail verdict for the feature as a whole.

### Commits Examined
Hash and message for each commit attributed to the feature, and any flagged for unrelated content.

### Requirements Checklist
One checklist per supplied analysis document. For each requirement: **Status** (PASS / FAIL / PARTIAL), **Evidence** (file path + line, or diff excerpt), **Notes** (deviations or concerns).

### Issues Found
Numbered list; each with **Severity** (CRITICAL / WARNING / INFO), the affected file(s)/line(s), and a suggested remediation.

### Unimplemented Requirements
Analysis items with no corresponding change in the delivered commits.

### Out-of-Scope Changes
Changes present in the feature's commits that the analysis doesn't account for.
