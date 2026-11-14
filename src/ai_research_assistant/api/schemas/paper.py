
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class PaperResponse(BaseModel):

    model_config = ConfigDict(from_attributes=True)

    id: int
    arxiv_id: str
    title: str
    published: datetime | None
    pdf_link: str | None
    received_at: datetime | None
