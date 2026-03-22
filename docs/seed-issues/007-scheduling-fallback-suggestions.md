# Issue: Suggest in-hours fallback windows for scheduling

Labels:
- candidate-task
- difficulty:medium
- area:scheduling
- area:api

## Summary

Improve the caller response for ambiguous or off-hours scheduling requests by suggesting acceptable business-hour fallback windows instead of only returning a generic manual-review note.

## Requirements

- preserve the existing route contract,
- keep non-blind scheduling behavior,
- make suggestions deterministic in tests,
- add tests for ambiguous and off-hours cases,
- document the tradeoff.

## Acceptance criteria

- invalid or ambiguous requests are not blindly confirmed,
- the response gives useful in-hours guidance,
- tests cover at least three edge cases.
