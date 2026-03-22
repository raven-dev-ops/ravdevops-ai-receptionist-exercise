from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path


@dataclass(frozen=True)
class KnowledgeChunk:
    chunk_id: int
    text: str


@lru_cache(maxsize=8)
def _load_chunks_cached(path: str, modified_time: int) -> tuple[KnowledgeChunk, ...]:
    file_path = Path(path)
    raw = file_path.read_text(encoding="utf-8").strip()
    if not raw:
        return ()

    chunks = [block.strip() for block in raw.split("\n\n") if block.strip()]
    return tuple(KnowledgeChunk(chunk_id=index + 1, text=chunk) for index, chunk in enumerate(chunks))


def load_chunks(path: str) -> list[KnowledgeChunk]:
    file_path = Path(path)
    if not file_path.exists():
        return []

    return list(_load_chunks_cached(str(file_path.resolve()), int(file_path.stat().st_mtime_ns)))
