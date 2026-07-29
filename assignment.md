# Week 8 – Exploring AI Code Review Using Graphite

## Assignment Overview

In this assignment, you will practice agent-driven development and AI-assisted code review on a more advanced codebase. You will implement the tasks in `week8/docs/TASKS.md`, validate your work with tests and manual review, and compare your own review notes with AI-generated code reviews.

## Get Started with Graphite

1. Sign up for Graphite: [https://app.graphite.dev/signup]
2. Upon sign up, you can claim your 30-day free trial.

## What to do

Implement the tasks from `week8/docs/TASKS.md` using an AI coding tool of your choice (e.g. Cursor, Copilot, Claude, etc.).

### For each task

   1. Create a separate branch.
   2. Implement the task with your AI tool using a 1-shot prompt.
   3. Manually review the changes line-by-line. Fix issues you notice and add explanatory commit messages where helpful.
   4. Open a Pull Request (PR) for the task. Ensure your PRs include:
      - Description of the problem and your approach.
      - Summary of testing performed (include commands and results) and any added/updated tests.
      - Notable tradeoffs, limitations, or follow-ups.
   5. Use Graphite to generate an AI-assisted code review on the PR.
   6. Document the results of your PR in the `writeup.md`.

## Deliverables

In your `writeup.md`, we are looking for the follwoing:

- Four PRs, one per completed task, each with:
  - Clear PR description
  - Links to relevant commits/issues.
  - Graphite review comments visible on the PR

- A brief reflection addressing the following:
  - The types of comments you typically made in your manual reviews (e.g., correctness, performance, security, naming, test gaps, API shape, UX, docs).
  - A comparison of **your** comments vs. **Graphite’s** AI-generated comments for each PR.
  - When the AI reviews were better/worse than yours (cite specific examples)
  - Your comfort level trusting AI reviews going forward and any heuristics for when to rely on them.
