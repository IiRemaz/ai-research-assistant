
import os
import tempfile
from pathlib import Path

from sqlalchemy.orm import Session

from ai_research_assistant.storage.paper_repository import (
    get_or_extract_paper_text
)

from ai_research_assistant.storage.paper_chunk_repository import (
    save_chunks
)

from ai_research_assistant.rag.chunking import split_into_chunks
from ai_research_assistant.rag.embedding import generate_embeddings

from ai_research_assistant.rag.vector_store import (
    create_vector_store,
    save_index
)


PROJECT_ROOT = Path(__file__).resolve().parents[3]
INDEX_DIR = PROJECT_ROOT / "data" / "vector_indexes"


def get_index_path(paper_id: int) -> Path:
    return INDEX_DIR / f"paper_{paper_id}.index"


def index_paper(
    session: Session,
    paper_id: int,
    chunk_size: int = 500,
    overlap: int = 50
):

    # 1. Retrieve or extract the paper text
    paper_text = get_or_extract_paper_text(
        session=session,
        paper_id=paper_id
    )

    if not paper_text or not paper_text.strip():
        raise ValueError("Paper text is empty.")

    # 2. Split the text into chunks
    chunks = split_into_chunks(
        paper_text,
        chunk_size=chunk_size,
        overlap=overlap
    )

    if not chunks:
        raise ValueError("No chunks were generated.")

    # 3. Generate embeddings
    embeddings = generate_embeddings(chunks)

    # 4. Create a new FAISS index
    new_index = create_vector_store(embeddings)

    # 5. Prepare the index directory and temporary file
    INDEX_DIR.mkdir(parents=True, exist_ok=True)

    index_path = get_index_path(paper_id)

    temp_file = tempfile.NamedTemporaryFile(
        suffix=".index",
        prefix=f"paper_{paper_id}_",
        dir=INDEX_DIR,
        delete=False
    )

    staging_path = Path(temp_file.name)
    temp_file.close()

    committed = False

    try:
        # 6. Save the new FAISS index to a staging file
        save_index(
            new_index,
            staging_path
        )

        # 7. Save chunks in the database
        save_chunks(
            session=session,
            paper_id=paper_id,
            chunks=chunks
        )

        # 8. Commit database changes
        session.commit()
        committed = True

        # 9. Replace the old index with the new one
        os.replace(
            staging_path,
            index_path
        )

    except Exception:
        if not committed:
            session.rollback()
        else:
            # The database is committed, but the index replacement failed.
            # Remove the old index to prevent retrieving incorrect chunks.
            if index_path.exists():
                index_path.unlink()

        raise

    finally:
        # Remove the staging file if it still exists
        if staging_path.exists():
            staging_path.unlink()

    return new_index
