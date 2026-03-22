# Issue: Suppress duplicate appointment creation

Labels:
- candidate-task
- difficulty:medium
- area:scheduling
- area:data

## Summary

Repeated or replayed inbound requests should not blindly create duplicate appointments for the same caller and normalized time.

## Requirements

- preserve the existing API route,
- define a clear duplicate rule,
- keep manual-review states explainable,
- add tests for repeated requests,
- document the tradeoff.

## Acceptance criteria

- duplicate appointment rows are not created for equivalent requests,
- manual-review behavior remains explicit,
- CI passes.
