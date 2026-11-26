
"""
Phase 12: BM25 keyword retrieval over ChromaDB documents.

Features:
- Reads the existing ChromaDB collection
- Preserves document IDs and sources
- Implements BM25 without additional dependencies
- Does not modify or re-embed documents
"""

import math
import re
from collections import Counter
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class RetrievedChunk:
    chunk_id: str
    text: str
    source: str


def load_chroma_chunks(
    collection: Any,
    batch_size: int = 500,
) -> list[RetrievedChunk]:
    """Load stored text and metadata from a Chroma collection."""

    if batch_size < 1:
        raise ValueError("batch_size must be positive")

    chunks = []
    offset = 0

    while True:
        batch = collection.get(
            include=["documents", "metadatas"],
            limit=batch_size,
            offset=offset,
        )

        ids = batch.get("ids") or []
        texts = batch.get("documents") or []
        metadata = batch.get("metadatas") or []

        if not ids:
            break

        if len(ids) != len(texts) or len(ids) != len(metadata):
            raise ValueError("Incomplete ChromaDB batch")

        for chunk_id, text, meta in zip(
            ids, texts, metadata
        ):
            if not isinstance(text, str) or not text.strip():
                continue

            chunks.append(
                RetrievedChunk(
                    chunk_id=str(chunk_id),
                    text=text,
                    source=str(
                        (meta or {}).get("source", "unknown")
                    ),
                )
            )

        offset += len(ids)

        if len(ids) < batch_size:
            break

    return chunks


def tokenize(text: str) -> list[str]:
    """Convert text into lowercase searchable tokens."""
    return re.findall(r"\w+", text.lower())


class BM25Retriever:
    """Rank document chunks using BM25."""

    def __init__(
        self,
        chunks: list[RetrievedChunk],
        k1: float = 1.5,
        b: float = 0.75,
    ):
        if k1 <= 0:
            raise ValueError("k1 must be positive")

        if not 0 <= b <= 1:
            raise ValueError("b must be between 0 and 1")

        if len({c.chunk_id for c in chunks}) != len(chunks):
            raise ValueError("Duplicate chunk IDs detected")

        self.chunks = chunks
        self.k1 = k1
        self.b = b

        self.term_frequencies = [
            Counter(tokenize(chunk.text))
            for chunk in chunks
        ]

        self.document_lengths = [
            sum(freq.values())
            for freq in self.term_frequencies
        ]

        self.n_documents = len(chunks)

        self.avgdl = (
            sum(self.document_lengths) / self.n_documents
            if self.n_documents else 0.0
        )

        # Number of documents containing each term.
        self.document_frequency = Counter()

        for frequencies in self.term_frequencies:
            self.document_frequency.update(
                frequencies.keys()
            )

    def _score(self, query_terms: list[str], index: int) -> float:
        """Calculate BM25 score for one document."""

        frequencies = self.term_frequencies[index]
        document_length = self.document_lengths[index]

        score = 0.0

        for term in set(query_terms):
            frequency = frequencies.get(term, 0)

            if frequency == 0:
                continue

            document_frequency = self.document_frequency[term]

            idf = math.log(
                1.0
                + (
                    self.n_documents - document_frequency + 0.5
                ) / (document_frequency + 0.5)
            )

            normalization = (
                1 - self.b
                + self.b * document_length / self.avgdl
            )

            denominator = (
                frequency + self.k1 * normalization
            )

            score += idf * (
                frequency * (self.k1 + 1)
            ) / denominator

        return score

    def retrieve(
        self,
        question: str,
        top_k: int = 5,
    ) -> list[RetrievedChunk]:
        """Return the highest-ranked matching chunks."""

        if top_k < 1:
            raise ValueError("top_k must be positive")

        if not isinstance(question, str):
            raise TypeError("question must be a string")

        query_terms = tokenize(question)

        if not query_terms or not self.chunks:
            return []

        scores = [
            (self._score(query_terms, index), index)
            for index in range(self.n_documents)
        ]

        # Exclude documents without keyword matches.
        matching = [
            (score, index)
            for score, index in scores
            if score > 0
        ]

        matching.sort(
            key=lambda item: (-item[0], item[1])
        )

        return [
            self.chunks[index]
            for _, index in matching[:top_k]
        ]
