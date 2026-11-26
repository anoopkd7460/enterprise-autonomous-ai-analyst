
"""
Phase 12: Cross-Encoder document reranking.

Reorders hybrid retrieval candidates using a
pretrained question-passage relevance model.

The model is loaded lazily and reused.
"""

import math
from functools import lru_cache
from typing import Any

from app.rag.bm25_retriever import RetrievedChunk


MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L6-v2"


@lru_cache(maxsize=1)
def load_reranker_model() -> Any:
    """
    Load the cross-encoder once per Python process.

    First execution may download model weights.
    """

    from sentence_transformers import CrossEncoder

    return CrossEncoder(MODEL_NAME)


class CrossEncoderReranker:
    """
    Reorder retrieved chunks using question-passage scores.
    """

    def __init__(self, model: Any = None):
        self.model = model

    def _get_model(self) -> Any:
        if self.model is not None:
            return self.model

        return load_reranker_model()

    def rerank(
        self,
        question: str,
        chunks: list[RetrievedChunk],
        top_k: int = 4,
    ) -> list[RetrievedChunk]:
        """
        Rank chunks by cross-encoder relevance.

        Preserves chunk IDs and source metadata.
        """

        if not isinstance(question, str):
            raise TypeError("Question must be a string")

        if top_k < 1:
            raise ValueError("top_k must be positive")

        if not question.strip() or not chunks:
            return []

        # Each pair contains the question and one passage.
        pairs = [
            (question, chunk.text)
            for chunk in chunks
        ]

        # Predict model relevance scores.
        scores = self._get_model().predict(pairs)

        if len(scores) != len(chunks):
            raise ValueError(
                "Cross-encoder returned an invalid score count"
            )

        scored_chunks = []

        for index, (chunk, score) in enumerate(
            zip(chunks, scores)
        ):
            score = float(score)

            if not math.isfinite(score):
                raise ValueError(
                    "Cross-encoder returned a non-finite score"
                )

            scored_chunks.append(
                (score, index, chunk)
            )

        # Highest relevance score comes first.
        # Original order breaks ties deterministically.
        scored_chunks.sort(
            key=lambda item: (-item[0], item[1])
        )

        return [
            chunk
            for _, _, chunk in scored_chunks[:top_k]
        ]


def rerank_chunks(
    question: str,
    chunks: list[RetrievedChunk],
    top_k: int = 4,
) -> list[RetrievedChunk]:
    """
    Convenience function for future RAG integration.
    """

    reranker = CrossEncoderReranker()

    return reranker.rerank(
        question=question,
        chunks=chunks,
        top_k=top_k,
    )
