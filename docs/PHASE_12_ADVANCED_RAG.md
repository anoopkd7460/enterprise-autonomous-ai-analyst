
# Phase 12 — Advanced Retrieval-Augmented Generation

## 1. Objective

Improve the Enterprise Autonomous AI Analyst's document
retrieval architecture by combining semantic retrieval,
keyword retrieval, rank fusion and neural reranking.

Preserve compatibility with Phase 11 and Portfolio V1.

## 2. Architecture

User Question
    |
    v
Document Agent
    |
    v
ADVANCED_RAG_ENABLED
    |
    +-- false --> Existing ChromaDB Dense Retrieval
    |
    +-- true --> Advanced RAG
                   |
                   +-- ChromaDB Semantic Retrieval
                   |
                   +-- BM25 Keyword Retrieval
                   |
                   v
              Reciprocal Rank Fusion
                   |
                   v
              Cross-Encoder Reranking
                   |
                   v
              Source-Aware Evidence
                   |
                   v
              Existing LLM Answer Generation

## 3. Implementation Modules

### app/rag/fusion.py
Reciprocal Rank Fusion combines ranked candidate IDs.

### app/rag/bm25_retriever.py
BM25 keyword retrieval over existing ChromaDB documents.

### app/rag/hybrid_retriever.py
Combines dense and sparse retrieval using RRF.

### app/rag/reranker.py
Reranks question-passage pairs with a cross-encoder.

Model:
cross-encoder/ms-marco-MiniLM-L6-v2

### app/agents/document_agent.py
Selects the retrieval pipeline using a feature flag
and returns document answers with optional evidence metadata.

## 4. Feature Flags

ADVANCED_RAG_ENABLED=false

Default mode: existing ChromaDB retrieval.

ADVANCED_RAG_ENABLED=true

Advanced mode: dense retrieval, BM25, RRF and reranking.

ADVANCED_WORKFLOW_ENABLED is a separate Phase 11 flag.

## 5. Source Attribution

Advanced RAG preserves:
- chunk_id
- source filename
- retrieved passage text

DocumentAgentResult retains:
- question
- retrieved_chunks
- answer

Phase 12 adds:
- source_chunks

Existing callers remain compatible.

Source metadata identifies retrieved evidence. It does not
independently validate every generated claim or citation.

## 6. Validation

Development branch:
feature/phase-12-advanced-rag

Observed automated test result:
134 passed

Real retrieval evaluation:
- Indexed documents: 1 PDF
- Indexed chunks: 2
- Evaluation questions: 4
- Evidence integrity checks: 4 passed

The cross-encoder successfully loaded and ran on CPU.

A real Document Agent execution returned document metadata
and an answer citing an indexed source chunk.

## 7. Performance Observations

Observed local evaluation timings:

Dense retrieval: approximately 174–411 ms
BM25 retrieval: approximately 0.04–0.15 ms
Hybrid retrieval: approximately 182–210 ms

Cross-encoder:
- First call: approximately 6310 ms, including model loading
- Subsequent calls: approximately 37–56 ms

These are local observations, not production benchmarks.

## 8. Known Limitations

1. The evaluation corpus contains only two chunks.
2. Retrieval accuracy improvement has not been established.
3. An unrelated employee-policy question returned sales-report
   passages, demonstrating that retrieved evidence may be
   irrelevant.
4. No calibrated relevance threshold is implemented.
5. BM25 indexes are rebuilt from the ChromaDB corpus for
   each hybrid retrieval request.
6. Cross-encoder model initialization adds cold-start latency.
7. Source attribution is provided, but per-claim citation
   correctness is not automatically verified.

## 9. Testing

Run:

    python -m pytest -q

Run the evaluation:

    python -m scripts.evaluate_phase12_rag

Check Git changes:

    git diff --check

## 10. Deployment Status

Phase 12 is developed on a feature branch.

It has not been merged into main or deployed.

The ADVANCED_RAG_ENABLED flag is disabled by default.

Production deployment requires a separate review and approval.

## 11. Completion Criteria

- RRF implemented
- BM25 implemented
- Hybrid retrieval implemented
- Cross-encoder reranker implemented
- Source-aware results implemented
- Document Agent integrated
- Feature flag implemented
- Automated regression tests passed
- Local retrieval diagnostics completed
- Documentation recorded
- Feature branch committed and pushed
