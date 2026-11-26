
"""Phase 12 tests for BM25 retrieval."""

import pytest

from app.rag.bm25_retriever import (
    BM25Retriever,
    RetrievedChunk,
    load_chroma_chunks,
)


@pytest.fixture
def sample_chunks():
    return [
        RetrievedChunk(
            "report-0",
            "North India Q4 inventory shortage",
            "regional_report.pdf",
        ),
        RetrievedChunk(
            "report-1",
            "South India sales increased",
            "regional_report.pdf",
        ),
        RetrievedChunk(
            "report-2",
            "Employee leave policy and holidays",
            "company_policy.pdf",
        ),
    ]


def test_keyword_retrieval(sample_chunks):
    retriever = BM25Retriever(sample_chunks)

    results = retriever.retrieve(
        "North India inventory shortage"
    )

    assert results[0].chunk_id == "report-0"
    assert results[0].source == "regional_report.pdf"


def test_no_matching_keywords(sample_chunks):
    retriever = BM25Retriever(sample_chunks)

    assert retriever.retrieve("cryptocurrency") == []


def test_top_k_limit(sample_chunks):
    retriever = BM25Retriever(sample_chunks)

    results = retriever.retrieve("India", top_k=1)

    assert len(results) == 1


def test_empty_corpus():
    retriever = BM25Retriever([])

    assert retriever.retrieve("revenue") == []


def test_duplicate_chunk_ids(sample_chunks):
    with pytest.raises(ValueError):
        BM25Retriever(
            [sample_chunks[0], sample_chunks[0]]
        )


def test_invalid_top_k(sample_chunks):
    retriever = BM25Retriever(sample_chunks)

    with pytest.raises(ValueError):
        retriever.retrieve("revenue", top_k=0)


def test_chroma_document_loading():
    class FakeCollection:
        def get(self, include, limit, offset):
            if offset == 0:
                return {
                    "ids": ["doc-0", "doc-1"],
                    "documents": [
                        "North India sales",
                        "Revenue increased",
                    ],
                    "metadatas": [
                        {"source": "report.pdf"},
                        {"source": "report.pdf"},
                    ],
                }

            return {
                "ids": [],
                "documents": [],
                "metadatas": [],
            }

    chunks = load_chroma_chunks(
        FakeCollection(),
        batch_size=2,
    )

    assert len(chunks) == 2
    assert chunks[0].chunk_id == "doc-0"
    assert chunks[1].text == "Revenue increased"
