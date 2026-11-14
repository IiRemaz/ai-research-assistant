
from sqlalchemy.orm import Session

from ai_research_assistant.database import utc_now
from ai_research_assistant.models.paper import Paper
from ai_research_assistant.models.conversation import Conversation
from ai_research_assistant.models.message import Message


def create_conversation(
    session: Session,
    paper_id: int,
    title: str | None = None
) -> Conversation:

    paper = session.query(Paper).filter_by(id=paper_id).first()

    if paper is None:
        raise ValueError(
            f"Paper with ID {paper_id} was not found."
        )

    conversation = Conversation(
        paper_id=paper_id,
        title=title
    )

    session.add(conversation)
    session.flush()

    return conversation


def get_conversations_by_paper(
    session: Session,
    paper_id: int
) -> list[Conversation]:

    return (
        session.query(Conversation)
        .filter_by(paper_id=paper_id)
        .order_by(Conversation.created_at.desc())
        .all()
    )


def save_message(
    session: Session,
    conversation_id: int,
    role: str,
    content: str
) -> Message:

    if role not in ["user", "assistant"]:
        raise ValueError(
            "Role must be either 'user' or 'assistant'."
        )

    if not content or not content.strip():
        raise ValueError("Message content cannot be empty.")

    conversation = (
        session.query(Conversation)
        .filter_by(id=conversation_id)
        .first()
    )

    if conversation is None:
        raise ValueError(
            f"Conversation with ID {conversation_id} was not found."
        )

    message = Message(
        conversation_id=conversation_id,
        role=role,
        content=content
    )

    conversation.updated_at = utc_now()

    session.add(message)
    session.flush()

    return message


def get_conversation_messages(
    session: Session,
    conversation_id: int
) -> list[Message]:

    return (
        session.query(Message)
        .filter_by(conversation_id=conversation_id)
        .order_by(
            Message.created_at.asc(),
            Message.id.asc()
        )
        .all()
    )
