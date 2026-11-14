
from sqlalchemy.orm import Session
from ai_research_assistant.models.paper import Paper
from ai_research_assistant.models.paper_chunk import PaperChunk


def save_chunks(
    session: Session,
    paper_id: int,
    chunks: list[str]
) -> int:

    paper = session.query(Paper).filter_by(id=paper_id).first()

    if paper is None:
        raise ValueError(f"Paper with ID {paper_id} not found.")

    if any(not chunk or not chunk.strip() for chunk in chunks):
        raise ValueError("Chunks cannot contain empty text.")

    session.query(PaperChunk).filter_by(
        paper_id=paper_id
    ).delete(synchronize_session=False)

    chunk_records = [
        PaperChunk(
            paper_id=paper_id,
            chunk_index=index,
            content=content
        )
        for index, content in enumerate(chunks)
    ]

    session.add_all(chunk_records)
    session.flush()

    return len(chunk_records)


def get_chunks_by_paper(
    session: Session,
    paper_id: int
) -> list[PaperChunk]:

    return (
        session.query(PaperChunk)
        .filter_by(paper_id=paper_id)
        .order_by(PaperChunk.chunk_index.asc())
        .all()
    )


def delete_chunks_by_paper(
    session: Session,
    paper_id: int
) -> int:

    deleted_count = (
        session.query(PaperChunk)
        .filter_by(paper_id=paper_id)
        .delete(synchronize_session=False)
    )

    return deleted_count
