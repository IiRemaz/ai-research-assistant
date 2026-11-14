
from sqlalchemy.orm import Session

from ai_research_assistant.rag.embedding import generate_embeddings

from ai_research_assistant.rag.vector_store import (
    search_similar,
    load_index
)

from ai_research_assistant.rag.indexing import get_index_path

from ai_research_assistant.storage.paper_chunk_repository import (
    get_chunks_by_paper
)


def retrieve_relevant_chunks(
    session: Session,
    paper_id: int,
    query: str,
    top_k: int = 5
):

    # 1. Validate input
    if not query or not query.strip():
        raise ValueError("Query cannot be empty.")

    if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k <= 0:
        raise ValueError("top_k must be a positive integer.")

    # 2. Check whether the FAISS index exists
    index_path = get_index_path(paper_id)

    if not index_path.is_file():
        raise FileNotFoundError(
            f"Index for paper {paper_id} not found."
        )

    # 3. Load the FAISS index
    index = load_index(index_path)

    # 4. Retrieve stored chunks from the database
    stored_chunks = get_chunks_by_paper(
        session=session,
        paper_id=paper_id
    )

    if not stored_chunks:
        raise ValueError(
            f"No chunks found for paper {paper_id}."
        )

    # 5. Verify that the index and database are synchronized
    if index.ntotal != len(stored_chunks):
        raise RuntimeError(
            "FAISS index and database chunks are out of sync. "
            "Re-index the paper before retrieving."
        )

    # 6. Generate the query embedding
    query_embedding = generate_embeddings([query])[0]

    # 7. Search for similar vectors
    scores, indices = search_similar(
        index,
        query_embedding,
        top_k
    )

    # 8. Map FAISS positions to their corresponding database chunks
    results = []

    for score, chunk_position in zip(scores, indices):

        if chunk_position < 0:
            continue

        if chunk_position >= len(stored_chunks):
            continue

        chunk = stored_chunks[chunk_position]

        results.append({
            "chunk_index": chunk.chunk_index,
            "content": chunk.content,
            "score": float(score)
        })

    return results
