
def build_chat_prompt(
    question,
    retrieved_chunks,
    conversation_history=None
):
    if not question or not question.strip():
        raise ValueError("Question cannot be empty")

    if not retrieved_chunks:
        raise ValueError("Retrieved chunks cannot be empty")

    # 1. Define the assistant instructions
    instructions = """
You are an AI research assistant.

Answer the user's questions using only the provided research paper context.

Rules:
- Use the provided context as your primary source.
- Do not invent facts or information.
- If the context does not contain the answer, clearly say so.
- Explain technical concepts clearly.
- Maintain the language used by the user.
- Reference the relevant chunk numbers using [Chunk N].
"""

    # 2. Build the research paper context
    context_parts = []

    for chunk in retrieved_chunks:
        context_parts.append(
            f"[Chunk {chunk['chunk_index']}]\n"
            f"{chunk['content']}"
        )

    paper_context = "\n\n".join(context_parts)

    # 3. Build the previous conversation history
    history_parts = []

    if conversation_history:
        for message in conversation_history:
            history_parts.append(
                f"{message['role']}: {message['content']}"
            )

    conversation = "\n".join(history_parts)

    # 4. Combine everything into one prompt
    prompt = f"""
{instructions}

Research Paper Context:
{paper_context}

Previous Conversation:
{conversation if conversation else "No previous conversation."}

Current User Question:
{question}

Answer:
"""

    return prompt
