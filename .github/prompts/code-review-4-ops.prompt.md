---
name: 'code-review-4-ops'
description: 'Review code changes for non-developer roles (testers, operations). Optionally provide an issue reference (e.g. HB-12).'
model: Auto (copilot)
agent: 'agent'
argument-hint: 'Optionally provide an issue reference (e.g. HB-12)'
---

# Non-Developer Code Review

Review code changes and produce a structured summary for non-developer stakeholders (testers, operations, project managers).

## Gathering Changes

### Uncommitted changes (always)

Run `git diff` and `git diff --staged` in the terminal to collect all uncommitted changes.

### Issue-linked changes (when an HB-x reference is provided)

1. Run `git log --all --oneline --grep="HB-x"` (substitute the actual identifier) to find related commits.
2. For each commit hash, run `git show <hash>` to collect the full diff.
3. Combine with uncommitted changes for the complete picture.

If no issue reference is provided, skip this step.

## Output Format

Structure the review into exactly these sections:

### Summary

Brief plain-language overview of what changed and why.

### Changed Areas

List affected files, endpoints, and configuration files. Reference file names and endpoint paths. Do not explain code internals.

### Impact on Testing

What should testers focus on? Which test scenarios are affected or need to be created?

### Impact on Operations / Deployment

Configuration changes, new or modified environment variables, infrastructure implications, database migration needs.

### Risk Assessment

What could go wrong? What is the blast radius? Are there backward-compatibility concerns?

### Questions / Action Items

Anything unclear, incomplete, or requiring follow-up from the team.

## Tone

- Write for non-developers: reference file names, endpoints, config keys — skip code-level details unless asked
- Keep each section concise; the reader can ask follow-up questions for more detail
- No emoji
