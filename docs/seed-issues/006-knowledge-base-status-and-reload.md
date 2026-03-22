# Issue: Add knowledge-base status and reload tooling

Labels:
- candidate-task
- difficulty:medium
- area:retrieval
- area:api

## Summary

Add a safe, explainable way to inspect knowledge-base status and refresh loaded knowledge without restarting the whole service.

## Requirements

- define a small public or maintainer-facing interface,
- expose at least chunk count and source metadata,
- keep behavior deterministic in tests,
- update docs.

## Acceptance criteria

- a reviewer can tell whether the knowledge base is loaded and how large it is,
- refresh behavior is testable,
- CI passes.
