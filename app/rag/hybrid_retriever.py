
"""
Phase 12: Hybrid document retrieval.

Combines:
1. ChromaDB dense semantic retrieval
2. BM25 sparse keyword retrieval
3. Reciprocal Rank Fusion (RRF)

The original ChromaDB collection is not modified.
"""

from typing import Any

from app.rag.bm25_retriever import (
    BM25Retriever,
    RetrievedChunk,
    load_chroma_chunks,
)

from app.rag.fusion import reciprocal_rank_fusion


class HybridRetriever:
    """
    Retrieve and rank evidence from the same corpus
    using both dense and sparse retrieval.
    """

    def __init__(self, collection: Any):
        self.collection = collection

    def retrieve(
        self,
        question: str,
        top_k: int = 4,
        candidate_k: int = 10,
    ) -> list[RetrievedChunk]:
        """
        Retrieve top matching chunks using hybrid search.

        Args:
            question: Business question.
            top_k: Number of final returned chunks.
            candidate_k: Candidate count per retrieval method.

        Returns:
            RetrievedChunk objects with original IDs,
            document text, and source metadata.
        """

        if not isinstance(question, str):
            raise TypeError("question must be a string")

        if not question.strip():
            return []

        if top_k < 1:
            raise ValueError("top_k must be positive")

        if candidate_k < 1:
            raise ValueError("candidate_k must be positive")

        # Step 1: Read existing ChromaDB document chunks.
        chunks = load_chroma_chunks(self.collection)

        if not chunks:
            return []

        # Preserve metadata using unique chunk IDs.
        chunk_lookup = {
            chunk.chunk_id: chunk
            for chunk in chunks
        }

        # Step 2: Dense semantic retrieval.
        dense_limit = min(candidate_k, len(chunks))

        dense_response = self.collection.query(
            query_texts=[question],
            n_results=dense_limit,
            include=["documents", "metadatas"],
        )

        dense_ids = (
            (dense_response.get("ids") or [[]])[0]
        )

        # Only accept IDs present in the loaded corpus.
        dense_ids = [
            chunk_id
            for chunk_id in dense_ids
            if chunk_id in chunk_lookup
        ]

        # Step 3: Sparse BM25 keyword retrieval.
        bm25 = BM25Retriever(chunks)

        sparse_results = bm25.retrieve(
            question,
            top_k=candidate_k,
        )

        sparse_ids = [
            chunk.chunk_id
            for chunk in sparse_results
        ]

        # Step 4: Fuse rankings by unique chunk ID.
        fused_ids = reciprocal_rank_fusion(
            ranked_results=[
                dense_ids,
                sparse_ids,
            ],
            top_k=top_k,
        )

        # Step 5: Convert IDs back into full chunks.
        return [
            chunk_lookup[chunk_id]
            for chunk_id in fused_ids
        ]


def retrieve_hybrid_chunks(
    question: str,
    top_k: int = 4,
) -> list[RetrievedChunk]:
    """
    Convenience function for the application.

    This imports the existing collection lazily,
    avoiding an unnecessary ChromaDB initialization
    when the module is imported for unit tests.
    """

    from app.rag.vector_store import collection

    retriever = HybridRetriever(collection)

    return retriever.retrieve(
        question=question,
        top_k=top_k,
    )
