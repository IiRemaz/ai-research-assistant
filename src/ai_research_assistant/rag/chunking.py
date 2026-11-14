
import tiktoken


def split_into_chunks(paper_text, chunk_size=500, overlap=50):
    if not paper_text or not paper_text.strip():
        return []

    if chunk_size <= 0 or overlap < 0 or overlap >= chunk_size:
        raise ValueError("Invalid chunk_size or overlap")

    tokenizer = tiktoken.get_encoding("cl100k_base")

    tokens = tokenizer.encode(paper_text)

    _, offsets = tokenizer.decode_with_offsets(tokens)

    chunks = []

    step = chunk_size - overlap

    for start in range(0, len(tokens), step):
        end = min(start + chunk_size, len(tokens))

        char_start = offsets[start]

        if end < len(tokens):
            char_end = offsets[end]
        else:
            char_end = len(paper_text)

        chunk_text = paper_text[char_start:char_end]

        chunks.append(chunk_text)

    return chunks
