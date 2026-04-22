from __future__ import annotations

import json
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from .chunking import TextChunk

TOKEN_PATTERN = re.compile(r"[a-zA-Z0-9]{2,}")


def _tokenize(text: str) -> list[str]:
    return [token.lower() for token in TOKEN_PATTERN.findall(text)]


def _counter_norm(values: Counter[str]) -> float:
    return math.sqrt(sum(v * v for v in values.values()))


def _cosine(a: Counter[str], b: Counter[str]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(a[token] * b[token] for token in a.keys() & b.keys())
    denominator = _counter_norm(a) * _counter_norm(b)
    if denominator == 0:
        return 0.0
    return dot / denominator


@dataclass
class RetrievalMatch:
    source: str
    text: str
    score: float


class RetrievalIndex:
    def __init__(self, rows: list[dict]):
        self.rows = rows
        self._counters = [Counter(row.get("tokens", [])) for row in rows]

    @classmethod
    def from_chunks(cls, chunks: list[TextChunk]) -> "RetrievalIndex":
        rows = []
        for chunk in chunks:
            rows.append(
                {
                    "chunk_id": chunk.chunk_id,
                    "source": chunk.source,
                    "text": chunk.text,
                    "tokens": _tokenize(chunk.text),
                }
            )
        return cls(rows)

    @classmethod
    def load(cls, path: Path) -> "RetrievalIndex":
        payload = json.loads(path.read_text(encoding="utf-8"))
        return cls(payload.get("rows", []))

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"rows": self.rows}
        path.write_text(json.dumps(payload, ensure_ascii=True, indent=2), encoding="utf-8")

    def search(self, query: str, *, top_k: int = 4, min_score: float = 0.08) -> list[RetrievalMatch]:
        query_counter = Counter(_tokenize(query))
        scored: list[tuple[float, dict]] = []

        for idx, row in enumerate(self.rows):
            score = _cosine(query_counter, self._counters[idx])
            if score >= min_score:
                scored.append((score, row))

        scored.sort(key=lambda item: item[0], reverse=True)
        return [
            RetrievalMatch(source=row["source"], text=row["text"], score=round(score, 4))
            for score, row in scored[:top_k]
        ]
