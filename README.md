# RavDevOps AI Receptionist Exercise

Public RavDevOps candidate exercise for AI systems, retrieval, scheduling, and containerized backend delivery.

This repository is a **public coding exercise** used during RavDevOps technical interviews. The exercise is open for review, but **solution pull requests are only reviewed from invited candidate collaborators**. External drive-by PRs will be closed without review.

AI assistance is allowed. Candidates must still explain:
- what the AI generated,
- what they changed,
- what the AI got wrong,
- and how they verified the final implementation.

## Why this repo exists

RavDevOps publicly positions around software engineering, CI/CD, SRE, and platform engineering. The organization's public CRM work also emphasizes scheduling, analytics, integrations, and operational delivery. This exercise combines those themes in a constrained backend project:
- API design
- retrieval-backed responses
- scheduling logic
- persistence
- Docker-based execution
- CI validation

## Exercise brief

Build and improve a minimal AI receptionist service that can:
1. accept inbound call-like requests,
2. answer from a local knowledge base,
3. schedule follow-ups within business rules,
4. persist logs and appointments,
5. run in Docker,
6. and remain explainable under review.

## Contribution policy

Only invited candidate collaborators may submit solution PRs.

Before opening a PR:
1. claim an issue by commenting on it,
2. wait for maintainer acknowledgement,
3. create a branch from `main`,
4. implement the issue,
5. open a PR using the required template,
6. be prepared to explain your code and AI usage live.

Read these first:
- [Candidate guide](docs/CANDIDATE_GUIDE.md)
- [AI policy](docs/AI_POLICY.md)
- [Contributing](CONTRIBUTING.md)
- [Architecture](ARCHITECTURE.md)

## Quick start

```bash
cp .env.example .env
docker compose up --build
```

Local URLs:
- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`

## Run locally without Docker

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Run tests

```bash
pytest -q
```

## Repository layout

```text
app/                    FastAPI application
data/                   Knowledge base and SQLite data
docs/                   Candidate-facing and maintainer-facing public docs
scripts/                Utility scripts and repo checks
tests/                  Public baseline tests
wiki/                   GitHub wiki source pages
.github/                PR template, issue templates, workflows, repo config
```

## Seed issue backlog

Maintainers can publish the prepared issue set from [`docs/seed-issues/`](docs/seed-issues/). Candidates should work from assigned issues rather than implementing arbitrary changes.

## Interview expectations

Part B of the interview is an explanation exercise. You may be asked to walk through:
- request flow,
- retrieval design,
- scheduling decisions,
- Docker setup,
- tradeoffs,
- and AI-assisted code generation.

## License

This repository is public for review and interview exercise use. It is **not open source**. See [LICENSE.md](LICENSE.md).

## Contact

For access or logistics, contact `business@ravdevops.com`.
