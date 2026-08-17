"""
Splits long document text into smaller overlapping chunks.

Why chunk at all: LLMs (and embedding models) work best with small,
focused pieces of text rather than one giant blob. Overlap between
chunks prevents losing context that spans a chunk boundary.
"""
from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_text(text: str, chunk_size: int = 800, chunk_overlap: int = 150) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = chunk_size,
        chunk_overlap = chunk_overlap,
        separators=["\n\n","\n", ". ", " ", ""],
    )
    return splitter.split_text(text)