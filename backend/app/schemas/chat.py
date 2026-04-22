from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=2, max_length=2000)
    session_id: str | None = Field(default=None, max_length=128)


class SourceAttribution(BaseModel):
    source: str
    snippet: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    grounded: bool
    sources: list[SourceAttribution] = Field(default_factory=list)
