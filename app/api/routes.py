"""
FastAPI backend exposing the Planner Agent over HTTP.
This lets any client (web, mobile, another service) call the agent
without needing direct Python access to this codebase.
"""

from fastapi import FastAPI
from pydantic import BaseModel

from app.workflows.graph import answer_question
from app.database.db import seed_sample_data
from app.agents.document_agent import index_document

app = FastAPI(title="Enterprise AI Analyst API")

@app.on_event("startup")
def startup():
    seed_sample_data()
    index_document("data/sample/Q4_2024_Regional_Report.pdf", source_name="Q4_2024_Regional_Report")

class QuestionRequest(BaseModel):
    question: str

class AnswerResponse(BaseModel):
    answer: str

@app.post("/ask", response_model=AnswerResponse)
def ask(request: QuestionRequest):
    answer = answer_question(request.question)
    return AnswerResponse(answer=answer)

@app.get("/health")
def health():
    return {"status":"ok"}