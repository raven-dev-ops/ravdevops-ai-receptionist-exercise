# Issue: Run the container as a non-root user

Labels:
- candidate-task
- difficulty:medium
- area:devops

## Summary

Tighten the Docker runtime by running the application as a non-root user while preserving the current compose workflow and writable data volume.

## Requirements

- keep `docker compose up --build` working,
- preserve local data persistence,
- explain any file-permission tradeoffs,
- update docs if commands change.

## Acceptance criteria

- the image runs as a non-root user,
- compose still comes up cleanly,
- readiness behavior still works.
