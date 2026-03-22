# Contributing

This is a public interview exercise repository. The contribution model is intentionally restricted.

## Who may contribute

Only invited candidates may submit solution pull requests that will be reviewed.

Outside contributors may read the repository, but unsolicited solution PRs will be closed without review.

## Candidate workflow

1. Read:
   - `README.md`
   - `docs/CANDIDATE_GUIDE.md`
   - `docs/AI_POLICY.md`
2. Comment on the issue you want to claim.
3. Wait for a maintainer to acknowledge the claim.
4. Create a branch from `main`.

Recommended branch format:

```text
candidate/<issue-number>-short-slug
```

Example:

```text
candidate/17-timezone-aware-scheduling
```

5. Implement only the scoped issue unless the issue explicitly allows a broader refactor.
6. Run:
   - `pytest -q`
   - `python scripts/review_check.py`
   - `docker compose up --build`
7. Open a PR using the required template.
8. Be prepared to explain the implementation and AI usage in the interview.

## Allowed tools

AI tools are allowed.

That does **not** lower the explanation bar. Reviewers may ask:
- which code came from AI,
- why you kept or changed it,
- what was incorrect,
- and how you verified behavior.

## Expectations

Your PR should:
- reference the issue,
- keep changes scoped,
- include tests when behavior changes,
- update docs when behavior changes,
- avoid unrelated cleanup,
- pass CI.

## What not to do

Do not:
- submit generated code you cannot explain,
- bypass the issue process,
- remove disclosure requirements,
- introduce secrets or production credentials,
- rewrite the entire repo unless the issue requires it.

## Review standard

Merges are not guaranteed. This is an evaluation repo, not a public roadmap. A rejected PR may still represent a strong interview performance if the reasoning and explanation are sound.
