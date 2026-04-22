from fastapi import APIRouter

from ..schemas.chat import ChatRequest, ChatResponse
from ..services.chat_service import answer_question

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    return answer_question(payload.question)
