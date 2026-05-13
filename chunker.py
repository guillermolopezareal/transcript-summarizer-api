from typing import List

DEFAULT_CHUNK_WORDS = 500
DEFAULT_OVERLAP_WORDS = 50


def chunk_transcript(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_WORDS,
    overlap: int = DEFAULT_OVERLAP_WORDS,
) -> List[str]:
    words = text.split()
    if len(words) <= chunk_size:
        return [text]

    overlap = min(overlap, chunk_size // 2)
    chunks = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start += chunk_size - overlap

    return chunks
