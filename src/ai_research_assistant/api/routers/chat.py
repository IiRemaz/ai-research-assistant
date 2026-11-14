
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ai_research_assistant.database import get_db
from ai_research_assistant.models.conversation import Conversation

from ai_research_assistant.storage.conversation_repository import (
    create_conversation,
    get_conversations_by_paper,
    get_conversation_messages,
)

from ai_research_assistant.services.chat_service import (
    chat_with_paper,
)

from ai_research_assistant.api.schemas.chat import (
    ConversationCreate,
    ConversationResponse,
    ConversationHistoryResponse,
    ChatMessageRequest,
    ChatMessageResponse,
    MessageResponse,
)


router = APIRouter(
    prefix="/conversations",
    tags=["Conversations"]
)


@router.post("/", response_model=ConversationResponse)
def start_conversation(
    request: ConversationCreate,
    db: Session = Depends(get_db)
):
    try:
        conversation = create_conversation(
            session=db,
            paper_id=request.paper_id
        )

        db.commit()
        db.refresh(conversation)

        return conversation

    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=404,
            detail=str(error)
        )


@router.get(
    "/paper/{paper_id}",
    response_model=list[ConversationHistoryResponse]
)
def list_conversations(
    paper_id: int,
    db: Session = Depends(get_db)
):
    conversations = get_conversations_by_paper(
        session=db,
        paper_id=paper_id
    )

    return conversations


@router.get(
    "/{conversation_id}/messages",
    response_model=list[MessageResponse]
)
def get_messages(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    conversation = (
        db.query(Conversation)
        .filter_by(id=conversation_id)
        .first()
    )

    if conversation is None:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found."
        )

    messages = get_conversation_messages(
        session=db,
        conversation_id=conversation_id
    )

    return messages


@router.post(
    "/{conversation_id}/messages",
    response_model=ChatMessageResponse
)
def send_message(
    conversation_id: int,
    request: ChatMessageRequest,
    db: Session = Depends(get_db)
):
    try:
        result = chat_with_paper(
            session=db,
            paper_id=request.paper_id,
            conversation_id=conversation_id,
            question=request.question
        )

        db.commit()

        return ChatMessageResponse(
            conversation_id=result["conversation_id"],
            paper_id=result["paper_id"],
            answer=result["answer"],
            sources=result["sources"]
        )

    except ValueError as error:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except FileNotFoundError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Paper is not indexed yet. Index it before chatting.")

    except RuntimeError:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail="The AI service is temporarily unavailable."
        )
