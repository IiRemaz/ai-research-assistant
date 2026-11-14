
from sqlalchemy.orm import Session

from ai_research_assistant.storage.conversation_repository import (
    get_conversations_by_paper,
    get_conversation_messages,
    save_message
)

from ai_research_assistant.rag.retrieval import (
    retrieve_relevant_chunks
)

from ai_research_assistant.rag.prompt_builder import (
    build_chat_prompt
)

from ai_research_assistant.model_client import generate_content


def chat_with_paper(
    session: Session,
    paper_id: int,
    conversation_id: int,
    question: str
):

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    # 1. Verify that the conversation belongs to the requested paper
    conversations = get_conversations_by_paper(
        session=session,
        paper_id=paper_id
    )

    conversation_exists = any(
        conversation.id == conversation_id
        for conversation in conversations
    )

    if not conversation_exists:
        raise ValueError(
            "Conversation does not belong to this paper."
        )

    # 2. Retrieve previous conversation messages
    previous_messages = get_conversation_messages(
        session=session,
        conversation_id=conversation_id
    )

    history = [
        {
            "role": message.role,
            "content": message.content
        }
        for message in previous_messages
    ]

    # 3. Retrieve relevant paper chunks
    retrieved_chunks = retrieve_relevant_chunks(
        session=session,
        paper_id=paper_id,
        query=question,
        top_k=5
    )

    if not retrieved_chunks:
        raise ValueError("No relevant chunks found.")

    # 4. Build the prompt
    prompt = build_chat_prompt(
        question,
        retrieved_chunks,
        history
    )

    # 5. Generate the AI response
    response = generate_content(prompt)

    answer = response.text if response else None

    if not answer or not answer.strip():
        raise ValueError("AI returned an empty response.")

    # 6. Save both messages in the current database transaction
    save_message(
        session=session,
        conversation_id=conversation_id,
        role="user",
        content=question
    )

    save_message(
        session=session,
        conversation_id=conversation_id,
        role="assistant",
        content=answer
    )

    return {
        "conversation_id": conversation_id,
        "paper_id": paper_id,
        "answer": answer,
        "sources": retrieved_chunks
    }
