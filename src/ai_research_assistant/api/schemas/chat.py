
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ConversationCreate(BaseModel):
    paper_id: int


class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    paper_id: int


class ConversationHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    paper_id: int
    title: str | None
    created_at: datetime
    updated_at: datetime


class ChatMessageRequest(BaseModel):
    paper_id: int
    question: str


class SourceResponse(BaseModel):
    chunk_index: int
    content: str
    score: float


class ChatMessageResponse(BaseModel):
    conversation_id: int
    paper_id: int
    answer: str
    sources: list[SourceResponse]


class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    conversation_id: int
    role: str
    content: str
    created_at: datetime
