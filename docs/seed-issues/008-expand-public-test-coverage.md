# Issue: Expand public coverage for webhook and failure paths

Labels:
- candidate-task
- difficulty:easy
- area:api
- area:tests

## Summary

Add useful public tests around webhook form validation, readiness failure cases, and duplicate scheduling protections.

## Requirements

- keep tests deterministic,
- avoid hidden-review logic in the public suite,
- explain why the selected cases matter,
- keep CI stable.

## Acceptance criteria

- public coverage meaningfully improves,
- tests are readable and reliable,
- CI passes.
