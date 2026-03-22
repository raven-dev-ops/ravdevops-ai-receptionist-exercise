from __future__ import annotations

from app.config import settings
from app.services.kb_service import load_chunks


if __name__ == "__main__":
    chunks = load_chunks(settings.knowledge_base_path)
    print(f"Loaded {len(chunks)} knowledge chunks from {settings.knowledge_base_path}")
    for idx, chunk in enumerate(chunks, start=1):
        print(f"\n[{idx}]\n{chunk.text}")
