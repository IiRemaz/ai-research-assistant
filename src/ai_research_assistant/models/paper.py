
from sqlalchemy import Column, Integer, String, DateTime, Text, Index

from ai_research_assistant.database import Base


class Paper(Base):
    __tablename__ = "papers"

    id = Column(Integer, primary_key=True)

    arxiv_id = Column(
        String(100),
        unique=True,
        nullable=False
    )

    title = Column(String, nullable=False)

    published = Column(DateTime, nullable=True)

    pdf_link = Column(String, nullable=True)

    received_at = Column(DateTime, nullable=True)

    full_text = Column(Text, nullable=True)

    __table_args__ = (
        Index("ix_papers_published", "published"),
        Index("ix_papers_received_at", "received_at"),
    )
