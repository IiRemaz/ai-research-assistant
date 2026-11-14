
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    Index
)

from ai_research_assistant.database import Base, utc_now


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True)

    paper_id = Column(
        Integer,
        ForeignKey("papers.id"),
        nullable=False
    )

    title = Column(String(255), nullable=True)

    created_at = Column(
        DateTime,
        default=utc_now,
        nullable=False
    )

    updated_at = Column(
        DateTime,
        default=utc_now,
        onupdate=utc_now,
        nullable=False
    )

    __table_args__ = (
        Index("ix_conversations_paper_id", "paper_id"),
    )
