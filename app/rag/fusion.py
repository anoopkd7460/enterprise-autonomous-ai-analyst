
"""
Phase 12: Reciprocal Rank Fusion.

Combines ranked text chunks returned by multiple
retrievers without relying on their raw scores.
"""

from collections import defaultdict
from collections.abc import Sequence


def reciprocal_rank_fusion(
    ranked_results: Sequence[Sequence[str]],
    top_k: int = 5,
    rrf_k: int = 60,
) -> list[str]:
    """
    Fuse multiple ranked lists using Reciprocal Rank Fusion.

    Args:
        ranked_results:
            Ranked text chunks from each retrieval system.

        top_k:
            Maximum number of returned chunks.

        rrf_k:
            Smoothing constant for the RRF formula.

    Returns:
        Unique chunks ordered by descending RRF score.
    """

    if top_k < 1:
        raise ValueError("top_k must be positive")

    if rrf_k < 1:
        raise ValueError("rrf_k must be positive")

    scores: dict[str, float] = defaultdict(float)
    first_seen: dict[str, int] = {}

    for results in ranked_results:
        seen_in_retriever: set[str] = set()

        for rank, chunk in enumerate(results, start=1):
            if not isinstance(chunk, str):
                raise TypeError("Retrieved chunks must be strings")

            if not chunk.strip():
                continue

            # Do not count duplicate hits from one retriever
            # more than once.
            if chunk in seen_in_retriever:
                continue

            seen_in_retriever.add(chunk)

            if chunk not in first_seen:
                first_seen[chunk] = len(first_seen)

            scores[chunk] += 1.0 / (rrf_k + rank)

    # Stable tie-breaking makes results reproducible.
    sorted_chunks = sorted(
        scores,
        key=lambda chunk: (
            -scores[chunk],
            first_seen[chunk],
        ),
    )

    return sorted_chunks[:top_k]
