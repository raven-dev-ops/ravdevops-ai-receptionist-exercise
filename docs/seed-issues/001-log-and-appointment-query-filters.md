# Issue: Add query filters to logs and appointments

Labels:
- candidate-task
- difficulty:medium
- area:api
- area:data
- area:observability

## Summary

Add optional query filters so reviewers can isolate logs and appointments by caller or request path without scanning the full collection.

## Requirements

- preserve the existing default route behavior,
- add optional query parameters for at least `request_id` and `caller_id`,
- keep the endpoints readable and deterministic,
- add tests,
- update docs if response behavior changes.

## Acceptance criteria

- a reviewer can narrow `/logs` and `/appointments` to a specific request or caller,
- the unfiltered routes still behave as they do today,
- CI passes.
