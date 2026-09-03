# Enterprise Autonomous AI Analyst

An industry-oriented **AI Data Analyst platform** that allows users to ask business questions in natural language and receive data-driven answers using SQL analytics, document retrieval, dataset analysis, and automated visualizations.

The platform combines **LLMs, LangChain, LangGraph, RAG, SQL, deterministic analytics, Redis caching, FastAPI, Streamlit, and Docker** into a modular production-style architecture.

---

## 🚀 Live Demo

| Component | Link |
|---|---|
| 🌐 Streamlit Frontend | https://enterprise-autonomous-ai-analyst.streamlit.app |
| ⚡ FastAPI Backend | https://enterprise-autonomous-ai-analyst-api.onrender.com |
| 📚 API Documentation | https://enterprise-autonomous-ai-analyst-api.onrender.com/docs |
| 💻 GitHub Repository | https://github.com/anoopkd7460/enterprise-autonomous-ai-analyst |

---

# 📌 Problem Statement

Traditional data analysis often requires users to:

1. Understand database schemas.
2. Write SQL queries.
3. Manually analyze uploaded datasets.
4. Search through business reports and documents.
5. Create visualizations separately.
6. Interpret the results before making business decisions.

This creates a gap between **business questions** and **actionable insights**.

The goal of this project is to build an AI-powered analyst that allows a user to ask questions in natural language and automatically determine how the question should be answered.

For example:

> **"What are the top 5 products by sales?"**

or

> **"Why did revenue decline in North India?"**

The system determines whether the question requires structured data analysis, document-based reasoning, dataset analysis, or a combination of sources.

---

# 💡 Solution

The **Enterprise Autonomous AI Analyst** uses an agentic architecture where different components specialize in different analytical tasks.

The system can:

- Convert natural-language questions into SQL.
- Execute safe read-only SQL queries.
- Analyze uploaded CSV and Excel datasets.
- Automatically profile datasets.
- Perform deterministic statistical analysis.
- Generate appropriate charts.
- Search business documents using RAG.
- Use embeddings and a vector database for semantic retrieval.
- Route analytical tasks through LangGraph.
- Use an LLM for reasoning and explanation.
- Cache repeated analytical requests using Redis.
- Expose the system through a FastAPI backend.
- Provide a user-friendly Streamlit interface.

---

# 🏗️ High-Level Architecture

```text
                         ┌──────────────────────┐
                         │        User          │
                         │ Natural Language     │
                         │      Question        │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    Streamlit UI      │
                         │   User Interaction   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │     FastAPI API      │
                         │   /api/v1/analyze    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   LangGraph Workflow │
                         │   Analysis Routing   │
                         └──────────┬───────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
              ▼                     ▼                     ▼
      ┌──────────────┐      ┌───────────────┐      ┌──────────────┐
      │  SQL Agent   │      │ Dataset Agent │      │ Document/RAG │
      │              │      │               │      │    Agent     │
      └──────┬───────┘      └───────┬───────┘      └──────┬───────┘
             │                      │                     │
             ▼                      ▼                     ▼
      ┌──────────────┐      ┌───────────────┐      ┌──────────────┐
      │ SQLite / SQL │      │ Pandas +      │      │ ChromaDB +   │
      │   Database   │      │ Analytics     │      │ Embeddings   │
      └──────────────┘      └───────────────┘      └──────────────┘
             │                      │                     │
             └──────────────────────┼─────────────────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    LLM Reasoning     │
                         │ Explanation + Insight │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    Redis Cache       │
                         │ Repeated Questions   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Final Answer + Chart │
                         └──────────────────────┘
```

---

# 🤖 AI Architecture

The project is built around several AI components.

## 1. Large Language Model

The LLM is responsible for tasks such as:

- Understanding natural-language questions.
- Generating SQL.
- Selecting analytical tools.
- Explaining analytical results.
- Generating business-oriented insights.
- Answering questions using retrieved document context.

The project uses **Groq with an OpenAI-compatible interface** and the configured model:

```text
openai/gpt-oss-20b
```

The LLM is intentionally separated from business logic so that the provider/model can be changed without redesigning the complete application.

---

# 🔗 LangChain

LangChain is used as the application framework for integrating the LLM with tools and analytical components.

Important concepts used in the project include:

- LLM integration
- Prompt templates
- Tool calling
- Structured analytical workflows
- Document processing
- Retrieval
- Embeddings

The key engineering principle is:

> **The LLM reasons about what should be done, while deterministic Python/SQL components perform the actual computation.**

This reduces the risk of hallucinated numerical results.

---

# 🧠 LangGraph

LangGraph is used to organize the analytical workflow as a state-based graph.

Conceptually:

```text
                 User Question
                       │
                       ▼
              ┌─────────────────┐
              │ Analysis Router │
              └────────┬────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
    SQL Route     Dataset Route    RAG Route
        │              │              │
        └──────────────┼──────────────┘
                       │
                       ▼
                Result Processing
                       │
                       ▼
                 Final Response
```

This provides a foundation for an agentic system where analytical responsibilities can be separated into specialized components.

---

# 🗄️ SQL Analytics

The SQL analytics component converts natural-language questions into SQL queries.

Example:

```text
User:
"Which region generated the highest sales?"
```

The LLM generates an appropriate SQL query based on the available schema.

The query is then executed against the database.

The result is passed back to the reasoning layer, which converts the raw database result into an understandable business answer.

---

# 🔐 SQL Safety

Because an LLM generates SQL dynamically, SQL execution must be protected.

The system follows a defense-in-depth approach.

### Prompt-level protection

The LLM is instructed to generate read-only analytical queries.

### Code-level protection

The execution layer validates the query and allows only safe query types such as:

```sql
SELECT ...
```

and:

```sql
WITH ...
SELECT ...
```

Operations such as:

```sql
DROP
DELETE
UPDATE
INSERT
ALTER
TRUNCATE
```

are not permitted through the analytical query execution path.

This ensures that an LLM failure cannot directly translate into destructive database operations.

---

# 📊 Dataset Analytics

The platform also supports uploaded CSV and Excel datasets.

The workflow is:

```text
CSV / Excel Upload
        │
        ▼
Dataset Loader
        │
        ▼
Dataset Validation
        │
        ▼
Dataset Profiler
        │
        ▼
Analytical Tool Selection
        │
        ▼
Deterministic Analysis
        │
        ▼
Chart Generation
        │
        ▼
LLM Explanation
        │
        ▼
Final Insight
```

---

# 🔎 Dataset Profiling

Before analysis, the system creates a dataset profile containing information such as:

- Number of rows.
- Number of columns.
- Numeric columns.
- Categorical columns.
- Missing values.
- Data types.
- Basic dataset characteristics.

This gives the analytical agent context before selecting an appropriate analytical operation.

---

# 🧮 Deterministic Analytics Engine

The project does not ask the LLM to perform numerical calculations directly.

Instead, reusable Python analytics tools perform the computation.

Examples include:

### Group-by analysis

```text
group_by_metric()
```

### Summary statistics

```text
summary_statistics()
```

### Top-N analysis

```text
top_n()
```

### Trend analysis

```text
trend_analysis()
```

### Correlation analysis

```text
correlation()
```

The LLM selects the appropriate analytical operation and interprets its output.

---

# 📈 Automated Visualization

The system can generate charts from analytical results using Plotly.

For example:

```text
Question
   │
   ▼
"Top 5 products by sales"
   │
   ▼
Analytics Tool
   │
   ▼
Top-N Result
   │
   ▼
Plotly Chart
   │
   ▼
Streamlit Visualization
```

Charts are generated from actual analytical results rather than fabricated values.

---

# 📚 RAG Architecture

The project includes a document-question-answering capability using Retrieval-Augmented Generation.

The RAG pipeline follows:

```text
Business Document
       │
       ▼
Document Loader
       │
       ▼
Text Extraction
       │
       ▼
Chunking
       │
       ▼
Embedding Model
       │
       ▼
Vector Database
     ChromaDB
       │
       ▼
Semantic Retrieval
       │
       ▼
Relevant Context
       │
       ▼
LLM
       │
       ▼
Grounded Answer
```

---

# 🔢 Embeddings

Embeddings convert text into numerical vectors that capture semantic meaning.

For example:

```text
"revenue decline"
```

and:

```text
"sales dropped"
```

can be represented as vectors with similar semantic characteristics.

The vector representation allows the system to search for relevant information based on meaning rather than exact keyword matching.

The project uses local sentence-transformer embeddings.

---

# 🧠 Vector Database

ChromaDB is used as the vector store for document retrieval.

Its responsibility is to:

- Store document embeddings.
- Store associated text chunks.
- Perform similarity search.
- Return the most relevant context for a user question.

This enables semantic retrieval before the LLM generates the final response.

---

# ✍️ Prompt Engineering

Prompt engineering is an important part of the system.

Prompts are designed to provide the LLM with:

- Clear role definition.
- Available schema/context.
- Analytical constraints.
- Output expectations.
- Safety rules.
- Grounding requirements.

A simplified conceptual prompt structure is:

```text
ROLE
You are an enterprise data analyst.

CONTEXT
Here is the database schema / analytical result / retrieved context.

TASK
Answer the user's business question.

CONSTRAINTS
Use only the provided information.
Do not invent numerical values.
Do not generate unsafe SQL.

OUTPUT
Return a concise business-oriented explanation.
```

The project therefore demonstrates practical prompt engineering rather than using a generic single prompt.

---

# ⚙️ Separation of AI Reasoning and Computation

One of the most important architectural decisions is separating **reasoning** from **computation**.

```text
              LLM
               │
        Decision / Reasoning
               │
               ▼
       ┌───────────────┐
       │ Deterministic │
       │    Tools      │
       └───────┬───────┘
               │
        Actual Computation
               │
               ▼
       Reliable Analytical
            Result
               │
               ▼
              LLM
        Explanation Layer
```

For example:

The LLM can decide:

> "Use top-N analysis on the Sales column."

But Python calculates the actual top five products.

This improves reliability and makes the system easier to test.

---

# ⚡ Redis Caching

Redis is used to reduce repeated computation.

The cache key considers:

```text
User Question
      +
Dataset Hash
```

Therefore, the same question against the same dataset can reuse a previous result.

The dataset hash is generated from deterministic DataFrame characteristics including:

- Values.
- Index.
- Column names.
- Data types.

The application is also designed to **gracefully degrade** when Redis is unavailable.

In that case:

```text
Redis Available
      │
      ├── Yes → Use Cache
      │
      └── No  → Continue Without Cache
```

The analytical system remains functional.

---

# ⚡ FastAPI Backend

FastAPI provides the production-style API layer.

Current API prefix:

```text
/api/v1
```

## Health Check

```text
GET /api/v1/health
```

Example response:

```json
{
  "status": "healthy",
  "service": "enterprise-autonomous-ai-analyst"
}
```

## Analysis Endpoint

```text
POST /api/v1/analyze
```

It accepts:

- A natural-language question.
- An optional CSV/Excel file.

The API returns structured information including:

- Final answer.
- Analytical result.
- Chart data when available.
- Dataset metadata when a file is uploaded.

---

# 🖥️ Streamlit Frontend

Streamlit provides the user-facing interface.

The frontend is intentionally kept thin.

```text
Streamlit
    │
    │ HTTP Request
    ▼
FastAPI Backend
    │
    ▼
AI/Data Analysis
    │
    ▼
Structured Response
    │
    ▼
Streamlit
```

The frontend is responsible for:

- Question input.
- Dataset upload.
- Backend health status.
- Answer rendering.
- Dataset summary.
- Chart rendering.
- User-friendly error messages.

The analytical logic remains inside the backend.

---

# 🛡️ Error Handling

Production-style error handling has been implemented across the system.

Examples include:

### Invalid dataset

```text
400 Bad Request
```

### LLM failure

```text
503 Service Unavailable
```

### Analysis timeout

```text
504 Gateway Timeout
```

### Backend unavailable

The Streamlit frontend displays a structured error instead of crashing.

### Redis failure

The application continues without caching.

This approach improves reliability and user experience.

---

# 🧪 Testing

The project includes automated tests covering important application components.

The current test suite contains:

```text
70 tests passed
```

Testing areas include:

- Dataset loading.
- Dataset validation.
- Analytics tools.
- Cache service.
- SQL functionality.
- API behavior.
- CSV upload integration.
- Chart generation.
- LLM failure handling.
- Error handling.

The goal is to ensure that individual components and important end-to-end workflows behave predictably.

---

# 🐳 Docker

The backend is containerized using Docker.

The Docker workflow is:

```text
Dockerfile
    │
    ▼
Python 3.12 Environment
    │
    ▼
Install requirements
    │
    ▼
Copy application
    │
    ▼
Run Uvicorn
    │
    ▼
FastAPI Backend
```

The application exposes:

```text
8000
```

The backend can be started with:

```bash
docker build -t enterprise-ai-analyst .
docker run -p 8000:8000 --env-file .env enterprise-ai-analyst
```

---

# 📁 Project Structure

```text
enterprise-autonomous-ai-analyst/
│
├── app/
│   ├── agents/
│   │   └── data_analyst_agent.py
│   │
│   ├── analytics/
│   │   ├── analysis_tools.py
│   │   ├── chart_generator.py
│   │   └── profiler.py
│   │
│   ├── api/
│   │   ├── main.py
│   │   ├── routes.py
│   │   └── schemas.py
│   │
│   ├── core/
│   │   └── config.py
│   │
│   ├── database/
│   │   └── ...
│   │
│   ├── llm/
│   │   └── ...
│   │
│   ├── rag/
│   │   └── ...
│   │
│   ├── services/
│   │   └── cache_service.py
│   │
│   └── workflows/
│       └── graph.py
│
├── streamlit_app/
│   ├── app.py
│   ├── api_client.py
│   │
│   ├── components/
│   │   ├── sidebar.py
│   │   ├── upload.py
│   │   ├── question_input.py
│   │   ├── answer_display.py
│   │   ├── chart_display.py
│   │   └── dataset_summary.py
│   │
│   └── utils/
│       └── config.py
│
├── data/
│   └── sample/
│
├── tests/
│
├── Documentation/
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

# 🧩 Module Responsibilities

| Module | Responsibility |
|---|---|
| `agents/` | AI analytical agents |
| `analytics/` | Deterministic dataset analysis |
| `api/` | FastAPI backend |
| `database/` | Database connectivity and SQL execution |
| `llm/` | LLM integration |
| `rag/` | Document retrieval pipeline |
| `services/` | Application services such as caching |
| `workflows/` | LangGraph orchestration |
| `streamlit_app/` | User interface |
| `tests/` | Automated testing |
| `Documentation/` | Project documentation |

This modular architecture makes components easier to test, maintain, replace, and extend.

---

# 🔄 End-to-End Workflow

```text
                     User Question
                           │
                           ▼
                    Streamlit UI
                           │
                           ▼
                    FastAPI API
                           │
                           ▼
                  LangGraph Workflow
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
          SQL Agent    Dataset Agent   RAG Agent
             │             │             │
             ▼             ▼             ▼
         SQL DB        Pandas Tools    ChromaDB
             │             │             │
             └─────────────┼─────────────┘
                           │
                           ▼
                    LLM Reasoning
                           │
                           ▼
                    Business Answer
                           │
                    ┌──────┴──────┐
                    │             │
                    ▼             ▼
                 Chart         Redis
                    │             │
                    └──────┬──────┘
                           ▼
                     User Interface
```

---

# 📊 Example SQL Analysis

### User Question

```text
What is the total sales?
```

### System Workflow

```text
Natural Language Question
          │
          ▼
       SQL Agent
          │
          ▼
Generate SELECT Query
          │
          ▼
      SQL Database
          │
          ▼
   Numerical Result
          │
          ▼
   LLM Explanation
          │
          ▼
     Final Answer
```

---

# 📈 Example Dataset Analysis

### User Question

```text
What are the top 5 products by sales?
```

### Workflow

```text
CSV Upload
    │
    ▼
Dataset Validation
    │
    ▼
Dataset Profiling
    │
    ▼
LLM Selects Analysis Tool
    │
    ▼
top_n()
    │
    ▼
Actual Sales Calculation
    │
    ▼
Plotly Visualization
    │
    ▼
LLM Explanation
    │
    ▼
Answer + Chart
```

---

# 📚 Example RAG Analysis

### User Question

```text
What caused the decline in regional sales?
```

### Workflow

```text
Question
   │
   ▼
Embedding
   │
   ▼
Vector Similarity Search
   │
   ▼
Relevant Document Chunks
   │
   ▼
LLM
   │
   ▼
Grounded Business Explanation
```

---

# 🏭 Deployment Architecture

The deployed system uses separate frontend and backend services.

```text
                   Internet User
                        │
                        ▼
        ┌────────────────────────────┐
        │     Streamlit Cloud        │
        │       Frontend              │
        └─────────────┬──────────────┘
                      │ HTTPS
                      ▼
        ┌────────────────────────────┐
        │          Render            │
        │      FastAPI Backend       │
        └─────────────┬──────────────┘
                      │
          ┌───────────┼───────────┐
          │           │           │
          ▼           ▼           ▼
       Groq API     SQLite      Upstash
        LLM         Database      Redis
```

---

# ☁️ Deployment Stack

| Component | Platform |
|---|---|
| Frontend | Streamlit Community Cloud |
| Backend | Render |
| LLM | Groq |
| Cache | Upstash Redis |
| Database | SQLite |
| Containerization | Docker |
| Source Control | GitHub |

The frontend communicates with the backend using the environment variable:

```text
ANALYST_API_URL
```

---

# 🔐 Environment Configuration

The project uses environment variables for configuration.

Example:

```text
GROQ_API_KEY=your_groq_api_key_here
LLM_MODEL=openai/gpt-oss-20b

APP_ENV=development

DATABASE_URL=sqlite:///./data/sample/sales.db

REDIS_ENABLED=false
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_SSL=false
REDIS_CONNECT_TIMEOUT=1.0
REDIS_SOCKET_TIMEOUT=1.0
```

Secrets are not hard-coded into the source code.

The `.env` file is excluded from version control.

---

# ▶️ Local Setup

## 1. Clone the Repository

```bash
git clone https://github.com/anoopkd7460/enterprise-autonomous-ai-analyst.git
cd enterprise-autonomous-ai-analyst
```

## 2. Create Virtual Environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### macOS / Linux

```bash
python -m venv .venv
source .venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure Environment Variables

### Windows

```bash
copy .env.example .env
```

### macOS / Linux

```bash
cp .env.example .env
```

Then add your API credentials to `.env`.

## 5. Start FastAPI

```bash
python -m uvicorn app.api.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

## 6. Start Streamlit

Open another terminal and run:

```bash
python -m streamlit run streamlit_app/app.py
```

The Streamlit interface will be available at:

```text
http://localhost:8501
```

---

# 🧠 Example Questions

The application can handle questions such as:

```text
What is the total sales?
```

```text
Which region has the highest sales?
```

```text
Which product generated the highest revenue?
```

```text
What are the top 5 products by sales?
```

```text
Show the sales trend over time.
```

```text
What caused the decline in regional sales?
```

The system determines the appropriate analytical path based on the question and available data.

---

# 🧱 Engineering Principles

The project follows several software engineering principles.

### Modular Architecture

Each responsibility is separated into dedicated modules.

### Separation of Concerns

AI reasoning, computation, API logic, UI, caching, and configuration are separated.

### Reusable Components

Analytics functions and services are designed to be reused across workflows.

### Defense in Depth

Critical operations such as SQL execution are protected at multiple levels.

### Graceful Degradation

Optional infrastructure such as Redis does not become a single point of failure.

### Configuration Through Environment Variables

Deployment-specific settings are not hard-coded.

### Automated Testing

Important components are validated through an automated test suite.

### Production-Oriented API Design

FastAPI provides structured request/response handling and HTTP error semantics.

---

# 🎯 Key Technical Skills Demonstrated

This project demonstrates practical experience with:

- Python
- SQL
- Pandas
- NumPy
- LangChain
- LangGraph
- Large Language Models
- Prompt Engineering
- Retrieval-Augmented Generation
- Embeddings
- ChromaDB
- FastAPI
- Streamlit
- Redis
- SQLite
- SQLAlchemy
- Plotly
- Docker
- Git
- GitHub
- REST APIs
- Automated Testing
- Cloud Deployment
- AI Agent Architecture
- Data Analytics
- Data Visualization

---

# 💼 Why This Project Is Industry-Relevant

The project combines several areas that are increasingly used in modern data and AI applications:

```text
Data Analytics
      +
SQL
      +
LLMs
      +
Agentic Workflows
      +
RAG
      +
Data Visualization
      +
APIs
      +
Caching
      +
Cloud Deployment
      +
Testing
```

Instead of building a standalone chatbot, the project demonstrates how an LLM can be integrated with real data, analytical tools, databases, retrieval systems, APIs, and production infrastructure.

---

# ⚠️ Current Limitations

The project is designed as a strong portfolio and interview project, but it also has realistic limitations.

- SQLite is used for the current sample database.
- The deployed environment is optimized for portfolio demonstration rather than high-scale enterprise workloads.
- LLM output quality depends on the selected model and available context.
- Complex analytical questions may require additional domain-specific tools.
- Production enterprise deployments would require stronger authentication, authorization, observability, monitoring, and database infrastructure.

These limitations are intentionally documented rather than hidden.

---

# 📌 Current Project Status

```text
✅ SQL Analytics Agent
✅ Document Q&A / RAG
✅ LangGraph Workflow
✅ Dataset Analytics
✅ Automated Visualization
✅ Redis Caching
✅ FastAPI Backend
✅ Streamlit Frontend
✅ Automated Testing
✅ Docker Support
✅ Cloud Deployment
✅ Project Documentation
```

The application is currently deployed and accessible through the live demo links above.

---

# 📖 Documentation

Detailed technical documentation is available in:

```text
Documentation/
└── Project Documentation.md
```

The documentation explains:

- Architecture
- AI components
- LangChain
- LangGraph
- RAG
- Embeddings
- Vector databases
- SQL safety
- Dataset analytics
- Redis
- FastAPI
- Streamlit
- Docker
- Deployment
- Testing
- Engineering decisions

---

# 👨‍💻 Author

**Anoop Kumar Dwivedi**

MCA — Data Science & Informatics  
National Institute of Technology, Patna

---

# 📜 License

This project is intended for educational, portfolio, and demonstration purposes.
