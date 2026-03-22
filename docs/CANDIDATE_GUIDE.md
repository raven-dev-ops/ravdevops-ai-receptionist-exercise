# Candidate Guide

## Goal

Your goal is to solve one or more scoped issues in this repository and then explain your reasoning during the interview.

## What you should assume

- The repo is intentionally small.
- Some starter implementations are conservative rather than sophisticated.
- Not every TODO is an invitation to rewrite the whole system.
- Reviewers care about correctness, reasoning, and explainability more than volume of code.

## Allowed

- Python packages that are reasonable for the scoped issue
- Docker changes
- Additional tests
- Refactors that are directly justified by the issue
- AI-assisted development

## Required

You must be able to explain:
- what changed,
- why it changed,
- how you verified it,
- and where AI helped.

## Recommended workflow

1. Pull latest `main`.
2. Create a new branch.
3. Read the issue carefully.
4. Write or update tests first when practical.
5. implement the minimum complete solution,
6. run:
   - `pytest -q`
   - `python scripts/review_check.py`
   - `docker compose up --build`
7. update docs if behavior changed,
8. open a PR using the required template.

## What interviewers are looking for

- Can you ship a scoped improvement cleanly?
- Do you understand request flow and data flow?
- Can you reason about retrieval and bounded uncertainty?
- Can you avoid over-engineering?
- Can you explain AI-generated code honestly?

## Common mistakes

- Solving a different problem than the issue asks for
- Turning one issue into a full rewrite
- Using AI output without verification
- Adding external secrets to make the solution run
- Removing conservative behavior and introducing hallucinations
