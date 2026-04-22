from __future__ import annotations

import json
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from .config import get_settings
from .retrieval.chunking import TextChunk, chunk_text
from .retrieval.index import RetrievalIndex


def _extract_visible_text_from_url(url: str) -> str:
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    for tag in soup(["script", "style", "noscript"]):
        tag.extract()

    return soup.get_text(separator=" ", strip=True)


def _read_sources(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    sources = payload.get("sources", [])
    if not isinstance(sources, list):
        raise ValueError("content_sources.json must contain a 'sources' list")
    return sources


def build_index() -> int:
    settings = get_settings()
    sources = _read_sources(settings.content_sources_path)
    all_chunks: list[TextChunk] = []

    for source in sources:
        source_id = source.get("id") or source.get("url") or source.get("path")
        source_type = source.get("type")
        if not source_id or source_type not in {"url", "text"}:
            continue

        text = ""
        if source_type == "url":
            text = _extract_visible_text_from_url(source["url"])
        elif source_type == "text":
            text = source.get("content", "")

        all_chunks.extend(chunk_text(text=text, source=source_id))

    index = RetrievalIndex.from_chunks(all_chunks)
    index.save(settings.index_path)
    return len(all_chunks)


if __name__ == "__main__":
    chunk_count = build_index()
    print(f"Indexed {chunk_count} chunks into retrieval store.")
