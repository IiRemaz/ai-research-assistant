from typing import Literal

from pydantic import BaseModel


class SummaryRequest(BaseModel):
    language: Literal["Arabic", "English"]


class SummaryResponse(BaseModel):
    paper_id: int
    content: str
    language: str