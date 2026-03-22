# Issue: Add replay-aware webhook validation

Labels:
- candidate-task
- difficulty:hard
- area:security
- area:api

## Summary

Extend the Twilio-compatible validation path so stale or replayed requests can be rejected in a deterministic, testable exercise mode.

## Requirements

- keep local development workable,
- avoid hard-coding secrets,
- define a configurable request-age tolerance,
- add tests,
- document how exercise-mode replay protection differs from production.

## Acceptance criteria

- stale or replayed signed requests can be rejected in tests,
- valid signed requests still work,
- docs explain the chosen rule.
