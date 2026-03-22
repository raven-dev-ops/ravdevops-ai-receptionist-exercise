# Architecture

## Purpose

The exercise application is intentionally small but structured like a production service:
- FastAPI API layer
- grounded local retrieval
- scheduling decision service
- SQLAlchemy persistence
- request tracing
- Dockerized execution

## Request lifecycle

1. `POST /incoming-call` receives JSON with `caller_id` and `message`.
2. `POST /twilio/incoming-call` accepts a Twilio-style form payload and can enforce exercise-mode signature validation when configured.
3. The knowledge base service loads chunked business context from `data/knowledge_base.txt`.
4. The retrieval service builds deterministic local hashed TF-IDF style vectors and ranks the best-supported chunks.
5. The response service builds a grounded answer:
   - if relevant context exists, answer from it,
   - otherwise prefer bounded uncertainty instead of invention.
6. The scheduling service detects follow-up requests, normalizes explicit times in the configured business timezone, and stores normalized UTC timestamps for persisted appointments.
7. The persistence layer writes:
   - call log,
   - request ID,
   - retrieved context,
   - retrieval diagnostics,
   - AI response,
   - optional appointment.
8. The API returns a structured response with request tracing and retrieval details.

## Design choices

### Why no external LLM key is required
The repository must run for every candidate without external secrets. Retrieval and response assembly are deterministic and local so the exercise remains portable and inspectable.

### Why deterministic local retrieval
The retriever is stronger than raw keyword overlap but still explainable in review. Candidates can inspect scored chunks, matched terms, and persisted diagnostics without needing hosted vector infrastructure.

### Why SQLite
SQLite keeps the exercise portable and easy to run in Docker. Candidates can still improve schema design, persistence behavior, and diagnostics.

### Why exercise-mode Twilio validation
The webhook path is designed to simulate secure inbound handling without requiring real production credentials or external telephony setup. Validation behavior is configurable so local development stays workable.

### Why visible baseline tests
Public tests establish minimum quality gates:
- health and readiness endpoints,
- endpoint contracts,
- bounded uncertainty,
- non-blind scheduling behavior,
- request tracing,
- and webhook validation flow.

Maintainers may use additional private evaluation steps during review.

## Current limitations

The application is still intentionally bounded:
- retrieval is local and deterministic, not model-hosted,
- appointment parsing covers common explicit requests, not full natural-language scheduling,
- no caller authentication or multi-tenant authorization model is included,
- Twilio signature validation is exercise-oriented and does not implement replay-window protection,
- and the knowledge base is file-backed rather than externally managed.

Those gaps are deliberate. Candidates solve them through scoped GitHub issues.

## Module overview

```text
app/main.py                          app bootstrap and request middleware
app/routes/                          API routes
app/services/call_flow_service.py    shared inbound-call orchestration
app/services/kb_service.py           knowledge base loading and chunking
app/services/rag_service.py          deterministic retrieval scoring
app/services/response_service.py     grounded answer assembly
app/services/scheduler_service.py    request-time parsing and validation
app/services/twilio_service.py       Twilio-compatible webhook validation
app/services/health_service.py       readiness and dependency checks
app/services/logging_service.py      persistence helpers
app/services/observability_service.py request IDs and structured logging
app/models/db_models.py              SQLAlchemy tables
app/schemas.py                       request/response models
```
