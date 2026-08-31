from fastapi import FastAPI

from app.api.routes import router


app = FastAPI(
    title="Enterprise Autonomous AI Analyst",
    description=(
        "AI-powered business analytics platform "
        "using LangGraph, LangChain, SQL, RAG, "
        "and deterministic analytics."
    ),
    version='1.0.0',
)

app.include_router(router)


@app.get("/")
def root():
    return{
        "service": "Enterprise Autonomous AI Analyst",
        "status": "running",
        "docs": "/docs",
    }