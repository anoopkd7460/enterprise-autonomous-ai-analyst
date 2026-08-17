"""
Vector store: stores documents chunks as embeddings in ChromaDB, and 
retrieves the most relevant chunks for a given question.

Concept: an "Embedding" is a list of numbers representing the meaning of a 
piece of text. Similar meanings -> similar numbers. To find relevant chunks for a 
question, we embed the question too, and find the chunks whose embeddings are
numerically closest to it. 
"""
import chromadb
from chromadb.utils import embedding_functions

from app.utils.logger import get_logger

logger = get_logger(__name__)

# Persists to disk so you don't have to re-embed documents every run
chroma_client = chromadb.PersistentClient(path="data/processed/chroma_db")

# Free, local embedding model - runs on your machine, no API key needed
embedding_fn = embedding_functions.DefaultEmbeddingFunction()

collection = chroma_client.get_or_create_collection(
    name="documents",
    embedding_function=embedding_fn,
)


def add_chunks(chunks: list[str], source:str):
    '''Adds text chunks to the vector store, tagged with their source filename.'''
    ids = [f'{source}-{i}' for i in range(len(chunks))]
    metadatas = [{'source':source} for _ in chunks]
    collection.add(documents=chunks, ids=ids, metadatas=metadatas)
    logger.info(f'Added {len(chunks)} chunks from {source} to vector store.')


def is_source_indexed(source: str) -> bool:
    """Checks if a document has already been chunked+embedded, to avoid re-doing it."""
    existing = collection.get(where={"source": source}, limit=1)
    return len(existing["ids"]) > 0


def retrieve_relevant_chunks(question: str, top_k: int = 4) -> list[str]:
    """Returns the top_k most relevant chunks for a given question."""
    results = collection.query(query_texts=[question], n_results=top_k)
    return results["documents"][0] if results["documents"] else []