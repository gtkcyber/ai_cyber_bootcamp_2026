---
name: commit-hygiene
description: Use when writing a git commit message. Enforces the team format and splits unrelated changes into separate commits.
---

# commit-hygiene

Write commit messages that read well in `git log` and keep unrelated changes
apart. The agent already has git; this skill is the house standard around it.

## When to use

Before any `git commit`.

## Steps

1. Run `git diff --staged` and group the changes by intent.
2. If two unrelated intents are staged together, stop and suggest splitting
   them into separate commits.
3. Write a subject line of 50 characters or fewer, in the imperative mood
   ("Add", "Fix", "Refactor").
4. Write a body that explains the WHY behind the change. Wrap it at 72
   characters.
5. Pick a type prefix from `references/conventional-commits.md`.

## Output

A ready-to-use commit message. When changes should be split, list the
proposed commits instead of a single message.
