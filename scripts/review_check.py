#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "Dockerfile",
    "docker-compose.yml",
    "README.md",
    "ARCHITECTURE.md",
    "LICENSE.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "requirements.txt",
    "app/main.py",
    "docs/AI_POLICY.md",
    ".github/pull_request_template.md",
]

OPTIONAL_BUT_EXPECTED = [
    "tests",
    "data/knowledge_base.txt",
    "wiki/Home.md",
]

RAG_PATTERNS = [
    r"retrieve_context",
    r"knowledge",
    r"chunk",
    r"score",
    r"retriev",
]

PERSISTENCE_PATTERNS = [
    r"sqlalchemy",
    r"create_all",
    r"sessionmaker",
    r"call_logs",
    r"appointments",
]

ROUTE_PATTERNS = [
    r"/incoming-call",
    r"/logs",
    r"/appointments",
    r"/health",
]

RED_FLAG_PATTERNS = [
    r"NotImplementedError",
]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def file_exists(rel_path: str) -> bool:
    return (ROOT / rel_path).exists()


def gather_text() -> str:
    chunks: list[str] = []
    for path in ROOT.rglob("*"):
        if path.is_file() and path.suffix in {".py", ".md", ".yml", ".yaml", ".txt", ".toml"}:
            chunks.append(read_text(path))
        elif path.is_file() and path.name == "Dockerfile":
            chunks.append(read_text(path))
    return "\n".join(chunks)


def count_matches(text: str, patterns: list[str]) -> int:
    count = 0
    for pattern in patterns:
        if re.search(pattern, text, flags=re.IGNORECASE | re.MULTILINE):
            count += 1
    return count


def main() -> int:
    print("=== RavDevOps Candidate Repo Auto-Check ===")
    failures: list[str] = []
    warnings: list[str] = []

    for rel in REQUIRED_FILES:
        if not file_exists(rel):
            failures.append(f"Missing required file: {rel}")

    for rel in OPTIONAL_BUT_EXPECTED:
        if not file_exists(rel):
            warnings.append(f"Missing expected item: {rel}")

    text = gather_text()

    if count_matches(text, ROUTE_PATTERNS) < 4:
        failures.append("Did not detect all required endpoints.")

    if count_matches(text, RAG_PATTERNS) < 3:
        failures.append("Weak or missing signs of a retrieval layer.")

    if count_matches(text, PERSISTENCE_PATTERNS) < 3:
        failures.append("Weak or missing signs of a persistence layer.")


    print("\nFailures:")
    if failures:
        for item in failures:
            print(f"- {item}")
    else:
        print("- None")

    print("\nWarnings:")
    if warnings:
        for item in warnings:
            print(f"- {item}")
    else:
        print("- None")

    result = 1 if failures else 0
    print(f"\nAUTO-CHECK RESULT: {'FAIL' if failures else 'PASS WITH REVIEW'}")
    return result


if __name__ == "__main__":
    raise SystemExit(main())
