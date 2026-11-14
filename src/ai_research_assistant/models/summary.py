
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    ForeignKey,
    UniqueConstraint
)

from ai_research_assistant.database import Base


class Summary(Base):
    __tablename__ = "summaries"

    id = Column(Integer, primary_key=True)

    paper_id = Column(
        Integer,
        ForeignKey("papers.id"),
        nullable=False
    )

    content = Column(Text, nullable=False)

    language = Column(String(20), nullable=False)

    model_name = Column(String(100), nullable=False)

    __table_args__ = (
        UniqueConstraint(
            "paper_id",
            "language",
            name="uq_paper_language"
        ),
    )
