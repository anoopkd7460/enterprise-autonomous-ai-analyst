"""
Planner: routes a question to the SQL Agent, the Document Agent, or both,
using LangGraph to define the workflow as a graph, then combines the
results into one final answer.
"""
from typing import TypedDict, Literal

from langgraph.graph import StateGraph, END

from app.agents.sql_agent import answer_question as sql_answer
from app.agents.document_agent import answer_question as doc_answer
from app.llm.client import chat
from app.utils.logger import get_logger

logger = get_logger(__name__)

ROUTER_SYSTEM_PROMPT = """You decide which data source(s) are needed to answer
a business question.

- "sql" -> question is about numbers/metrics from the sales database
  (revenue, units sold, comparisons, trends over time)
- "document" -> question is about reasons, context, or explanations that
  would come from reports/documents (why something happened, root causes,
  business context)
- "both" -> question needs numeric data AND contextual explanation

Reply with exactly one word: sql, document, or both.
"""


class PlannerState(TypedDict):
    question: str
    route: str
    sql_result: dict | None
    doc_result: dict | None
    final_answer: str


def route_question(state: PlannerState) -> PlannerState:
    question_lower = state["question"].lower()
    metric_words = ["revenue", "sales", "units", "profit", "growth"]
    reason_words = ["why", "reason", "cause", "root cause"]

    has_metric = any(w in question_lower for w in metric_words)
    has_reason = any(w in question_lower for w in reason_words)

    if has_metric and has_reason:
        route = "both"
        logger.info("Routed via heuristic (metric + reason word found): both")
    else:
        route = chat(ROUTER_SYSTEM_PROMPT, state["question"]).strip().lower()
        if route not in ("sql", "document", "both"):
            logger.warning(f"Unexpected route '{route}', defaulting to 'both'")
            route = "both"
        logger.info(f"Routed via LLM to: {route}")

    state["route"] = route
    return state


def call_sql_agent(state: PlannerState) -> PlannerState:
    result = sql_answer(state["question"])
    state["sql_result"] = {
        "explanation": result.explanation,
        "sql_query": result.sql_query,
    }
    return state


def call_document_agent(state: PlannerState) -> PlannerState:
    result = doc_answer(state["question"])
    state["doc_result"] = {"answer": result.answer}
    return state


def combine_answers(state: PlannerState) -> PlannerState:
    sql_part = state.get("sql_result")
    doc_part = state.get("doc_result")

    if sql_part and doc_part:
        prompt = (
            f"Question: {state['question']}\n\n"
            f"Data analysis finding:\n{sql_part['explanation']}\n\n"
            f"Document/context finding:\n{doc_part['answer']}\n\n"
            f"Combine these into one clear, unified answer for a business executive. "
            f"Merge overlapping points, don't just concatenate."
        )
        state["final_answer"] = chat(
            "You are a business analyst combining findings into one clear answer.",
            prompt,
        )
    elif sql_part:
        state["final_answer"] = sql_part["explanation"]
    elif doc_part:
        state["final_answer"] = doc_part["answer"]
    else:
        state["final_answer"] = "Could not generate an answer."

    return state


def decide_next(state: PlannerState) -> Literal["sql", "document", "both"]:
    return state["route"]


def build_graph():
    graph = StateGraph(PlannerState)

    graph.add_node("router", route_question)
    graph.add_node("sql_agent", call_sql_agent)
    graph.add_node("document_agent", call_document_agent)
    graph.add_node("combine", combine_answers)

    graph.set_entry_point("router")

    graph.add_conditional_edges(
        "router",
        decide_next,
        {
            "sql": "sql_agent",
            "document": "document_agent",
            "both": "sql_agent",  # if both, go sql first, then document
        },
    )

    # after sql_agent: if route was "both", go to document_agent next; else go straight to combine
    graph.add_conditional_edges(
        "sql_agent",
        lambda state: "document_agent" if state["route"] == "both" else "combine",
        {"document_agent": "document_agent", "combine": "combine"},
    )

    graph.add_edge("document_agent", "combine")
    graph.add_edge("combine", END)

    return graph.compile()


planner_graph = build_graph()


def answer_question(question: str) -> str:
    """Main entry point: runs the full planner workflow and returns the final answer."""
    result = planner_graph.invoke({
        "question": question,
        "route": "",
        "sql_result": None,
        "doc_result": None,
        "final_answer": "",
    })
    return result["final_answer"]