
"""
Document Agent with optional source-aware Advanced RAG.

Phase 12, Task 6:
Preserve source document metadata for retrieved evidence.
"""

import os
from dataclasses import dataclass, field

from app.rag.loaders import load_document
from app.rag.chunking import chunk_text
from app.rag.vector_store import (
    add_chunks,
    is_source_indexed,
    retrieve_relevant_chunks,
)
from app.rag.bm25_retriever import RetrievedChunk
from app.llm.client import chat
from app.utils.logger import get_logger


logger = get_logger(__name__)


DOC_SYSTEM_PROMPT = """
You are a business analyst.

Answer the user's question using ONLY the provided
document excerpts as context.

Rules:
- Do not invent facts or numerical values.
- Do not infer unsupported business causes.
- If evidence is insufficient, say so clearly.
- Keep the answer concise (2-4 sentences).
- Reference the supporting document findings.
- When source IDs are provided, cite the relevant
  evidence using its supplied source ID.
- Never invent a source filename or source ID.
"""


@dataclass
class DocumentAgentResult:
    question: str
    retrieved_chunks: list[str]
    answer: str

    # Added in Phase 12.
    # Default preserves the existing three-argument API.
    source_chunks: list[RetrievedChunk] = field(
        default_factory=list
    )


def is_advanced_rag_enabled() -> bool:
    """Advanced RAG is disabled by default."""

    return os.getenv(
        "ADVANCED_RAG_ENABLED",
        "false",
    ).strip().lower() in {"true", "1", "yes"}


def _retrieve_with_sources(
    question: str,
    top_k: int = 4,
) -> tuple[list[str], list[RetrievedChunk]]:
    """
    Return:
        (plain_text_chunks, source_aware_chunks)

    The original dense path preserves its behavior.
    Only Advanced RAG supplies trusted source metadata.
    """

    if top_k < 1:
        raise ValueError("top_k must be positive")

    if not is_advanced_rag_enabled():
        return (
            retrieve_relevant_chunks(question, top_k=top_k),
            [],
        )

    try:
        from app.rag.hybrid_retriever import (
            retrieve_hybrid_chunks,
        )
        from app.rag.reranker import rerank_chunks

        candidates = retrieve_hybrid_chunks(
            question,
            top_k=max(top_k * 3, 10),
        )

        if not candidates:
            return [], []

        ranked = rerank_chunks(
            question,
            candidates,
            top_k=top_k,
        )

        logger.info(
            "Advanced RAG retrieved %d source-aware chunks.",
            len(ranked),
        )

        return (
            [chunk.text for chunk in ranked],
            ranked,
        )

    except Exception as exc:
        logger.warning(
            "Advanced RAG failed (%s). "
            "Falling back to dense retrieval.",
            type(exc).__name__,
        )

        # Dense fallback currently returns text only.
        # Do not invent IDs or source filenames.
        return (
            retrieve_relevant_chunks(question, top_k=top_k),
            [],
        )


def retrieve_document_context(
    question: str,
    top_k: int = 4,
) -> list[str]:
    """
    Backward-compatible retrieval function.

    Existing callers still receive plain text.
    """

    texts, _ = _retrieve_with_sources(
        question,
        top_k=top_k,
    )

    return texts


def index_document(
    path: str,
    source_name: str | None = None,
):
    """Index a document if its source is not indexed."""

    source_name = source_name or path

    if is_source_indexed(source_name):
        logger.info(
            "%s already indexed, skipping.",
            source_name,
        )
        return

    text = load_document(path)
    chunks = chunk_text(text)

    add_chunks(
        chunks,
        source=source_name,
    )


def answer_question(question: str) -> DocumentAgentResult:
    """Generate an answer while preserving available evidence."""

    chunks, source_chunks = _retrieve_with_sources(
        question,
        top_k=4,
    )

    if not chunks:
        return DocumentAgentResult(
            question=question,
            retrieved_chunks=[],
            answer=(
                "No indexed documents found "
                "to answer this question."
            ),
            source_chunks=[],
        )

    if source_chunks:
        context_parts = []

        for chunk in source_chunks:
            context_parts.append(
                f"Source ID: {chunk.chunk_id}\n"
                f"Source Document: {chunk.source}\n"
                f"Excerpt:\n{chunk.text}"
            )

        context = "\n\n---\n\n".join(context_parts)

    else:
        # Original V1 context format.
        context = "\n\n---\n\n".join(chunks)

    prompt = (
        f"Document excerpts:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Answer:"
    )

    answer = chat(
        DOC_SYSTEM_PROMPT,
        prompt,
    )

    return DocumentAgentResult(
        question=question,
        retrieved_chunks=chunks,
        answer=answer,
        source_chunks=source_chunks,
    )
