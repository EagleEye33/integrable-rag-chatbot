from __future__ import annotations

from functools import lru_cache

from google import genai

from ..config import get_settings
from ..retrieval.index import RetrievalIndex
from ..schemas.chat import ChatResponse, SourceAttribution

FALLBACK_ANSWER = (
    "I could not find that information in the website or organization knowledge base yet. "
    "Please rephrase your question or contact support for exact details."
)


@lru_cache(maxsize=1)
def _load_index() -> RetrievalIndex:
    settings = get_settings()
    try:
        return RetrievalIndex.load(settings.index_path)
    except FileNotFoundError:
        return RetrievalIndex(rows=[])


def _build_prompt(question: str, context_blocks: list[dict]) -> str:
    context_text = "\n\n".join(
        [
            f"Source: {block['source']}\nContent: {block['text']}"
            for block in context_blocks
        ]
    )
    return (
        "You are a helpful assistant for website visitors.\n"
        "Use only the provided context to answer.\n"
        "If context is insufficient, respond exactly with: INSUFFICIENT_CONTEXT.\n\n"
        f"Question: {question}\n\n"
        f"Context:\n{context_text}"
    )


def answer_question(question: str) -> ChatResponse:
    settings = get_settings()
    matches = _load_index().search(
        question,
        top_k=settings.max_context_chunks,
        min_score=settings.min_relevance_score,
    )

    if not matches:
        return ChatResponse(answer=FALLBACK_ANSWER, grounded=False, sources=[])

    context_blocks = [
        {"source": match.source, "text": match.text, "score": match.score}
        for match in matches
    ]

    if not settings.gemini_api_key:
        # Safe fallback for local setup before API key is configured.
        return ChatResponse(
            answer=FALLBACK_ANSWER,
            grounded=False,
            sources=[
                SourceAttribution(source=block["source"], snippet=block["text"][:220], score=block["score"])
                for block in context_blocks
            ],
        )

    client = genai.Client(api_key=settings.gemini_api_key)
    prompt = _build_prompt(question=question, context_blocks=context_blocks)
    response = client.models.generate_content(model=settings.gemini_model, contents=prompt)
    model_answer = (response.text or "").strip()

    if not model_answer or model_answer == "INSUFFICIENT_CONTEXT":
        return ChatResponse(
            answer=FALLBACK_ANSWER,
            grounded=False,
            sources=[
                SourceAttribution(source=block["source"], snippet=block["text"][:220], score=block["score"])
                for block in context_blocks
            ],
        )

    return ChatResponse(
        answer=model_answer,
        grounded=True,
        sources=[
            SourceAttribution(source=block["source"], snippet=block["text"][:220], score=block["score"])
            for block in context_blocks
        ],
    )
