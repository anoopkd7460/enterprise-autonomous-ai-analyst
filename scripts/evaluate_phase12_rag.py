
"""
Phase 12 - Advanced RAG retrieval evaluation.

Compares:
1. ChromaDB dense retrieval
2. BM25 sparse retrieval
3. Hybrid retrieval with RRF
4. Hybrid retrieval with cross-encoder reranking

This script does not call the LLM.
It does not modify the indexed documents.
"""

from time import perf_counter

from app.rag.vector_store import (
    collection,
    retrieve_relevant_chunks,
)
from app.rag.bm25_retriever import (
    BM25Retriever,
    load_chroma_chunks,
)
from app.rag.hybrid_retriever import (
    retrieve_hybrid_chunks,
)
from app.rag.reranker import rerank_chunks


QUESTIONS = [
    "Why did North India sales decline in Q4 2024?",
    "How did the warehouse relocation affect sales?",
    "What was the impact of reduced marketing spending?",
    "What is the company's employee leave policy?",
]


def evaluate():
    chunks = load_chroma_chunks(collection)

    print("\nPHASE 12 ADVANCED RAG EVALUATION")
    print("=" * 65)
    print("Indexed chunks:", len(chunks))

    if not chunks:
        print("No documents indexed. Evaluation stopped.")
        return

    bm25 = BM25Retriever(chunks)

    # Display a warning about the small evaluation corpus.
    if len(chunks) < 10:
        print(
            "WARNING: Small corpus. "
            "Results are diagnostic, not an accuracy benchmark."
        )

    for question in QUESTIONS:
        print("\n" + "=" * 65)
        print("QUESTION:", question)

        # 1. Dense retrieval
        start = perf_counter()

        dense = retrieve_relevant_chunks(
            question,
            top_k=4,
        )

        dense_ms = (perf_counter() - start) * 1000

        # 2. BM25 retrieval
        start = perf_counter()

        sparse = bm25.retrieve(
            question,
            top_k=4,
        )

        sparse_ms = (perf_counter() - start) * 1000

        # 3. Hybrid retrieval
        start = perf_counter()

        hybrid = retrieve_hybrid_chunks(
            question,
            top_k=4,
        )

        hybrid_ms = (perf_counter() - start) * 1000

        # 4. Cross-encoder reranking
        start = perf_counter()

        reranked = rerank_chunks(
            question,
            hybrid,
            top_k=4,
        )

        rerank_ms = (perf_counter() - start) * 1000

        print(
            f"\nDense: {len(dense)} chunks "
            f"({dense_ms:.2f} ms)"
        )

        print(
            f"BM25: {len(sparse)} chunks "
            f"({sparse_ms:.2f} ms)"
        )

        print(
            f"Hybrid: {len(hybrid)} chunks "
            f"({hybrid_ms:.2f} ms)"
        )

        print(
            f"Reranking: {len(reranked)} chunks "
            f"({rerank_ms:.2f} ms)"
        )

        print(
            "\nBM25 IDs:",
            [chunk.chunk_id for chunk in sparse],
        )

        print(
            "Hybrid IDs:",
            [chunk.chunk_id for chunk in hybrid],
        )

        print(
            "Reranked IDs:",
            [chunk.chunk_id for chunk in reranked],
        )

        # Verify that reranking preserved the retrieved evidence.
        hybrid_ids = {
            chunk.chunk_id for chunk in hybrid
        }

        reranked_ids = [
            chunk.chunk_id for chunk in reranked
        ]

        assert len(reranked_ids) == len(set(reranked_ids)), (
            "Duplicate reranked evidence"
        )

        assert set(reranked_ids).issubset(hybrid_ids), (
            "Reranker introduced unknown evidence"
        )

        for chunk in reranked:
            assert chunk.source
            assert chunk.chunk_id
            assert chunk.text.strip()

        print("Evidence integrity: PASS")

    print("\n" + "=" * 65)
    print("PHASE 12 RETRIEVAL DIAGNOSTIC COMPLETED")


if __name__ == "__main__":
    evaluate()
