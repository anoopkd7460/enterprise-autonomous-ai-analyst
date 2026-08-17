"""
Document Agent: answers questions using RAG over indexed documents
(PDFs, Excel) instead of the SQL database.

Flow:
  question -> retrieve relevant chunks from vector store -> LLM answers
  using only those chunks as context
"""

from dataclasses import dataclass
from app.rag.loaders import load_document
from app.rag.chunking import chunk_text
from app.rag.vector_store import add_chunks, is_source_indexed, retrieve_relevant_chunks
from app.llm.client import chat
from app.utils.logger import get_logger


logger = get_logger(__name__)

DOC_SYSTEM_PROMPT = '''You are a business analyst. Answer the user's question using ONLY the 
provided document excerpts as context. If the excerpts don't contain enough information to answer, say so clearly instead of guessing.

Keep the answer concise(2-4 sentences) and cite which finding it's based on where relevant.
'''

@dataclass
class DocumentAgentResult:
    question: str
    retrieved_chunks: list[str]
    answer: str


def index_document(path: str, source_name: str| None=None):
    """Loads, chunks, and embeds a docuement - skips if already indexed."""
    source_name = source_name or path
    if is_source_indexed(source_name):
        logger.info(f'{source_name} already indexed, skipping.')
        return

    text = load_document(path)
    chunks = chunk_text(text)
    add_chunks(chunks, source = source_name)


def answer_question(question: str) -> DocumentAgentResult:
    chunks = retrieve_relevant_chunks(question, top_k=4)

    if not chunks:
        return DocumentAgentResult(
            question=question,
            retrieved_chunks=[],
            answer = 'No indexed documents found to answer this question.',
        )

    context = "\n\n---\n\n".join(chunks)
    prompt = f"Document excerpts:\n{context}\n\nQuestion: {question}\n\nAnswer:"
    answer = chat(DOC_SYSTEM_PROMPT, prompt)

    return DocumentAgentResult(
        question=question,
        retrieved_chunks=chunks,
        answer=answer,
    )