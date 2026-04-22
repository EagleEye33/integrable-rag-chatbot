from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TextChunk:
    chunk_id: str
    source: str
    text: str


def chunk_text(
    text: str,
    source: str,
    *,
    chunk_size: int = 700,
    overlap: int = 120,
) -> list[TextChunk]:
    clean_text = " ".join(text.split())
    if not clean_text:
        return []

    chunks: list[TextChunk] = []
    start = 0
    idx = 0

    while start < len(clean_text):
        end = min(start + chunk_size, len(clean_text))
        chunk_value = clean_text[start:end].strip()
        if chunk_value:
            chunks.append(
                TextChunk(
                    chunk_id=f"{source}::chunk-{idx}",
                    source=source,
                    text=chunk_value,
                )
            )
            idx += 1

        if end >= len(clean_text):
            break
        start = max(0, end - overlap)

    return chunks
