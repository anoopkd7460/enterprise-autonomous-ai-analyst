# Enterprise Autonomous AI Analyst

A multi-agent system that answers natural-language business questions
("Why did revenue fall in North India last quarter?") by querying a
sales database, reading business reports, and returning a plain-language
explanation with a recommendation — without a human writing SQL or
digging through documents manually.

## Example

**Question:** "Why did revenue fall in North India in Q4 2024?"

The system:
1. Routes the question to the right agent(s) — SQL, Document, or both
2. The **SQL Agent** writes and runs a query comparing Q4 vs Q3 revenue/units by product
3. The **Document Agent** retrieves relevant excerpts from a PDF report explaining root causes (distributor disruption, competitor discounts, marketing cuts)
4. Both findings are combined into one clear, executive-ready answer with a recommendation

## Architecture

                User Question
                     |
                     v
            Planner (LangGraph)
             [heuristic + LLM routing]
                     |
    +----------------+----------------+
    v                                 v

SQL Agent Document Agent
(LLM writes SQL, (RAG: chunks + embeds
runs it, self-corrects documents in ChromaDB,
on error) retrieves relevant chunks)
| |
+----------------+----------------+
v
Combine Answers (LLM)
|
v
Redis cache (repeat questions
skip the pipeline entirely)
|
+----------+----------+
v v
Streamlit UI FastAPI (/ask, /health)


## Tech stack

| Layer | Technology |
|---|---|
| LLM | Groq (`openai/gpt-oss-20b`), OpenAI-compatible API |
| Orchestration | LangGraph (multi-agent routing & state graph) |
| Structured data | SQLite + SQLAlchemy (Postgres-ready via connection string) |
| RAG | ChromaDB (vector store) + local sentence-transformer embeddings |
| Document parsing | pypdf, openpyxl |
| Backend | FastAPI |
| Frontend | Streamlit |
| Caching | Redis |
| Deployment | Docker |

## Key design decisions

- **Self-correcting SQL generation** — if the LLM's SQL fails to execute, the error is fed back to the LLM to retry (up to 2x) before failing, instead of crashing on the first bad query.
- **Hybrid routing** — a fast keyword heuristic catches clear "needs both data + context" cases (e.g. "why did revenue fall") without an extra LLM call; ambiguous questions fall back to LLM-based routing.
- **Defense in depth** — SQL safety is enforced both in the prompt (rules) and in code (`run_sql` blocks anything that isn't `SELECT`/`WITH`), so a prompt failure alone can't cause damage.
- **Provider-agnostic LLM layer** — all LLM calls go through one wrapper (`app/llm/client.py`), so swapping providers (currently Groq) touches one file, not the whole codebase.
- **SQLite for local dev, Postgres-ready** — the data layer uses SQLAlchemy, so switching to PostgreSQL for production is a one-line `DATABASE_URL` change, no code rewrite.
- **Graceful degradation** — if Redis isn't running, the app still works correctly, just without caching, instead of crashing.

## Project structure

enterprise-ai-analyst/
├── app/
│ ├── main.py # Streamlit UI
│ ├── agents/
│ │ ├── sql_agent.py # NL question -> SQL -> execute -> explain (with retry)
│ │ └── document_agent.py # RAG: retrieve + answer from indexed documents
│ ├── rag/
│ │ ├── loaders.py # PDF/Excel -> raw text
│ │ ├── chunking.py # text -> overlapping chunks
│ │ └── vector_store.py # ChromaDB embedding + retrieval
│ ├── workflows/
│ │ └── graph.py # LangGraph planner: routes, combines, caches
│ ├── database/
│ │ └── db.py # SQLAlchemy engine, sample data seeding, schema, safe query execution
│ ├── llm/
│ │ └── client.py # Provider-agnostic LLM wrapper (Groq via OpenAI SDK)
│ ├── api/
│ │ └── routes.py # FastAPI: /ask, /health
│ ├── services/
│ │ └── cache_service.py # Redis response caching
│ └── core/
│ └── config.py # Environment-based settings
├── data/sample/ # Auto-generated sample sales DB + sample PDF report
├── Dockerfile
├── requirements.txt
└── .env.example



## Getting started (if you're new to this project)

Follow these steps in order — no prior knowledge of the codebase needed.

### 1. Clone the repository
```bash
git clone https://github.com/anoopkd7460/enterprise-autonomous-ai-analyst.git
cd enterprise-autonomous-ai-analyst
```

### 2. Create and activate a virtual environment
```bash
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up your environment variables
```bash
copy .env.example .env          # Windows
# cp .env.example .env          # macOS/Linux
```
Open `.env` and add a free Groq API key (get one at [console.groq.com](https://console.groq.com), no credit card needed):


**Do not use quotes around values in `.env`** — write `GROQ_API_KEY=abc123`, not `GROQ_API_KEY="abc123"`.

### 5. Run the app
**Option A — Streamlit UI (recommended first run):**
```bash
python -m streamlit run app/main.py
```
This opens a browser at `http://localhost:8501`. A sample sales dataset and a sample PDF report are auto-generated and indexed on first run — no setup needed, just ask a question.

**Option B — FastAPI backend:**
```bash
python -m uvicorn app.api.routes:app --reload
```
Visit `http://127.0.0.1:8000/docs` for interactive API testing (Swagger UI).

### 6. (Optional) Enable Redis caching
Repeated questions get answered instantly instead of re-running the full pipeline.
```bash
docker run -d -p 6379:6379 --name redis-cache redis
```
If Redis isn't running, the app still works normally — caching is just skipped.

### 7. (Optional) Run fully containerized with Docker
```bash
docker build -t enterprise-ai-analyst .
docker run -p 8000:8000 --env-file .env enterprise-ai-analyst
```

## Try it out

Once running, ask questions like:
- "Why did revenue fall in North India in Q4 2024?"
- "Which product sold the most units overall?"
- "What caused the stock shortage in North India?"

The first two combine live data analysis with the second combines document-based reasoning — the Planner Agent automatically decides which source(s) each question needs.