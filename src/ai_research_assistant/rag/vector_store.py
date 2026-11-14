
import faiss
import numpy as np
import os
import tempfile
from pathlib import Path


def create_vector_store(embeddings):
    if len(embeddings) == 0:
        raise ValueError("Embeddings cannot be empty")

    embeddings = np.asarray(embeddings, dtype="float32")

    if embeddings.ndim != 2:
        raise ValueError("Embeddings must be a 2D array")

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    return index


def search_similar(index, query_embedding, top_k=3):
    if top_k <= 0:
        raise ValueError("top_k must be greater than zero")

    if index.ntotal == 0:
        return np.array([]), np.array([], dtype="int64")

    query_embedding = np.asarray(
        [query_embedding],
        dtype="float32"
    )

    scores, indices = index.search(query_embedding, top_k)

    valid_results = indices[0] != -1

    return scores[0][valid_results], indices[0][valid_results]


def save_index(index, file_path):
    file_path = Path(file_path)

    file_path.parent.mkdir(parents=True, exist_ok=True)

    # Convert FAISS index into binary data
    serialized_index = faiss.serialize_index(index)

    temp_path = None

    try:
        # Create a temporary file in the destination directory
        with tempfile.NamedTemporaryFile(
            mode="wb",
            dir=file_path.parent,
            prefix=f".{file_path.name}.",
            suffix=".tmp",
            delete=False
        ) as temp_file:

            temp_path = Path(temp_file.name)

            temp_file.write(serialized_index.tobytes())
            temp_file.flush()
            os.fsync(temp_file.fileno())

        # Replace destination only after successful writing
        os.replace(temp_path, file_path)

    except Exception:
        if temp_path is not None and temp_path.exists():
            temp_path.unlink()

        raise


def load_index(file_path):
    file_path = Path(file_path)

    if not file_path.is_file():
        raise FileNotFoundError(
            f"FAISS index file not found: {file_path}"
        )

    serialized_data = np.frombuffer(
        file_path.read_bytes(),
        dtype=np.uint8
    )

    if serialized_data.size == 0:
        raise ValueError("FAISS index file is empty")

    return faiss.deserialize_index(serialized_data)
