
from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey,
    UniqueConstraint,
    CheckConstraint,
    Index
)

from ai_research_assistant.database import Base


class PaperChunk(Base):
    __tablename__ = "paper_chunks"

    id = Column(Integer, primary_key=True)

    paper_id = Column(
        Integer,
        ForeignKey("papers.id"),
        nullable=False
    )

    chunk_index = Column(Integer, nullable=False)

    content = Column(Text, nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "paper_id",
            "chunk_index",
            name="uq_paper_chunk"
        ),
        CheckConstraint(
            "chunk_index >= 0",
            name="ck_chunk_index_nonnegative"
        ),
        Index(
            "ix_paper_chunks_paper_id",
            "paper_id"
        ),
    )
