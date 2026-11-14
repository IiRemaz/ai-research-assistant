
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    Index,
    CheckConstraint
)

from ai_research_assistant.database import Base, utc_now


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)

    conversation_id = Column(
        Integer,
        ForeignKey("conversations.id"),
        nullable=False
    )

    role = Column(String(20), nullable=False)

    content = Column(Text, nullable=False)

    created_at = Column(
        DateTime,
        default=utc_now,
        nullable=False
    )

    __table_args__ = (
        CheckConstraint(
            "role IN ('user', 'assistant')",
            name="ck_message_role"
        ),
        Index(
            "ix_messages_conversation_id",
            "conversation_id"
        ),
    )
