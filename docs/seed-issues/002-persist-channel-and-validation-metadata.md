# Issue: Persist inbound channel and validation metadata

Labels:
- candidate-task
- difficulty:medium
- area:data
- area:api
- area:security

## Summary

Distinguish direct API calls from Twilio-style webhook calls and persist enough metadata for a reviewer to understand how the request entered the system.

## Requirements

- extend persistence cleanly,
- store the inbound channel or adapter path,
- store validation outcome metadata without leaking secrets,
- update `/logs` if needed,
- add tests and docs.

## Acceptance criteria

- a reviewer can tell whether a call came from the direct JSON route or the Twilio-compatible route,
- validation state is inspectable after the fact,
- existing behavior remains intact.
