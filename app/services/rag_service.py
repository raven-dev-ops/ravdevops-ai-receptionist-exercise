from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from hashlib import blake2b
from math import log, sqrt
import re

from app.services.kb_service import KnowledgeChunk


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: int
    text: str
    score: float
    rank: int
    matched_terms: tuple[str, ...]
    retrieval_method: str = "local_hashed_tfidf"

    def to_diagnostic(self) -> dict[str, object]:
        return {
            "chunk_id": self.chunk_id,
            "score": round(self.score, 4),
            "rank": self.rank,
            "matched_terms": list(self.matched_terms),
            "retrieval_method": self.retrieval_method,
            "excerpt": self.text,
        }


TOKEN_RE = re.compile(r"[a-zA-Z0-9']+")
VECTOR_SIZE = 256
MIN_SCORE = 0.16
RELATIVE_SCORE_CUTOFF = 0.62
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "at",
    "be",
    "can",
    "do",
    "for",
    "from",
    "i",
    "in",
    "is",
    "it",
    "me",
    "my",
    "of",
    "on",
    "or",
    "please",
    "someone",
    "the",
    "to",
    "we",
    "what",
    "when",
    "you",
    "your",
}
TOKEN_ALIASES = {
    "api": "backend",
    "apis": "backend",
    "appointment": "schedule",
    "appointments": "schedule",
    "book": "schedule",
    "booking": "schedule",
    "business": "business",
    "callback": "schedule",
    "call": "schedule",
    "delivers": "delivery",
    "engineering": "software",
    "follow": "schedule",
    "followup": "schedule",
    "hours": "hours",
    "implementations": "implementation",
    "integrations": "integration",
    "outcomes": "delivery",
    "prices": "price",
    "refactors": "refactor",
    "scheduling": "schedule",
    "services": "service",
    "times": "time",
    "work": "delivery",
}


@dataclass(frozen=True)
class TextFeatures:
    weighted_features: dict[str, float]
    semantic_terms: tuple[str, ...]


def _normalize_token(token: str) -> str:
    token = token.lower().replace("'", "")
    if token.endswith("ies") and len(token) > 4:
        token = f"{token[:-3]}y"
    elif token.endswith("s") and len(token) > 4 and not token.endswith("ss"):
        token = token[:-1]
    return TOKEN_ALIASES.get(token, token)


def tokenize(text: str) -> set[str]:
    return {_normalize_token(token) for token in TOKEN_RE.findall(text)}


def _build_text_features(text: str) -> TextFeatures:
    semantic_terms = [token for token in tokenize(text) if token and token not in STOPWORDS]
    weighted_features: Counter[str] = Counter()

    for term in semantic_terms:
        weighted_features[f"tok:{term}"] += 1.0

    for left, right in zip(semantic_terms, semantic_terms[1:]):
        weighted_features[f"bi:{left}_{right}"] += 1.2

    collapsed = "".join(semantic_terms)
    for index in range(max(len(collapsed) - 2, 0)):
        trigram = collapsed[index : index + 3]
        if len(trigram) == 3:
            weighted_features[f"chr:{trigram}"] += 0.12

    return TextFeatures(weighted_features=dict(weighted_features), semantic_terms=tuple(semantic_terms))


def _build_idf(corpus: list[TextFeatures]) -> dict[str, float]:
    doc_frequency: Counter[str] = Counter()
    for item in corpus:
        doc_frequency.update(item.weighted_features.keys())

    total_docs = max(len(corpus), 1)
    return {
        feature: log((1 + total_docs) / (1 + count)) + 1.0
        for feature, count in doc_frequency.items()
    }


def _stable_hash(value: str) -> int:
    return int.from_bytes(blake2b(value.encode("utf-8"), digest_size=8).digest(), "big")


def _embed(features: TextFeatures, idf: dict[str, float]) -> list[float]:
    vector = [0.0] * VECTOR_SIZE
    for feature, tf in features.weighted_features.items():
        feature_hash = _stable_hash(feature)
        index = feature_hash % VECTOR_SIZE
        sign = -1.0 if (feature_hash // VECTOR_SIZE) % 2 else 1.0
        vector[index] += sign * ((1.0 + log(tf)) * idf.get(feature, 1.0))

    norm = sqrt(sum(item * item for item in vector))
    if norm == 0:
        return vector
    return [item / norm for item in vector]


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    return sum(left_item * right_item for left_item, right_item in zip(left, right))


def _matched_terms(query: TextFeatures, chunk: TextFeatures) -> tuple[str, ...]:
    overlap = sorted(set(query.semantic_terms).intersection(chunk.semantic_terms))
    return tuple(overlap[:6])


def retrieve_context(message: str, chunks: list[KnowledgeChunk], top_k: int = 2) -> list[RetrievedChunk]:
    if not chunks:
        return []

    query_features = _build_text_features(message)
    if not query_features.weighted_features:
        return []

    chunk_features = [_build_text_features(chunk.text) for chunk in chunks]
    idf = _build_idf(chunk_features)
    query_embedding = _embed(query_features, idf)

    scored: list[tuple[KnowledgeChunk, float, tuple[str, ...]]] = []
    for chunk, features in zip(chunks, chunk_features):
        score = _cosine_similarity(query_embedding, _embed(features, idf))
        if score <= 0:
            continue
        scored.append((chunk, score, _matched_terms(query_features, features)))

    scored.sort(key=lambda item: item[1], reverse=True)
    if not scored or scored[0][1] < MIN_SCORE:
        return []

    cutoff = max(MIN_SCORE, scored[0][1] * RELATIVE_SCORE_CUTOFF)
    results: list[RetrievedChunk] = []
    for rank, (chunk, score, matched_terms) in enumerate(scored, start=1):
        if score < cutoff:
            continue
        results.append(
            RetrievedChunk(
                chunk_id=chunk.chunk_id,
                text=chunk.text,
                score=score,
                rank=rank,
                matched_terms=matched_terms,
            )
        )
        if len(results) >= top_k:
            break

    return results
