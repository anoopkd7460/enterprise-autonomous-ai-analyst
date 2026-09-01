"""
Planner: routes a question to the SQL Agent, the Document Agent, or both,
using LangGraph to define the workflow as a graph, then combines the
results into one final answer.
"""

from typing import Literal, TypedDict

from langgraph.graph import END, StateGraph

from app.agents.data_analyst_agent import analyze_dataset
from app.agents.document_agent import answer_question as doc_answer
from app.agents.sql_agent import answer_question as sql_answer
from app.llm.client import chat
from app.services.cache_service import (
    get_cached_answer,
    set_cached_answer,
)
from app.utils.logger import get_logger, log_execution_time


logger = get_logger(__name__)


ROUTER_SYSTEM_PROMPT = """
You decide which data source is needed to answer a business question.

Available sources:

- "sql" -> questions about structured data stored in the SQL database,
  such as revenue, sales, units sold, profit, customer data,
  comparisons, and trends.

- "document" -> questions requiring information from business documents,
  reports, PDFs, policies, or other unstructured sources.

- "analytics" -> questions about a CSV or Excel dataset uploaded by the user,
  such as data profiling, statistics, patterns, top/bottom values,
  correlations, anomalies, trends, and business insights.

- "both" -> questions requiring both SQL data and document/context information.

Routing rules:

1. If the question clearly refers to the SQL database, choose "sql".
2. If the question clearly refers to uploaded CSV/Excel data, choose "analytics".
3. If the question requires information from reports/documents, choose "document".
4. If the question requires both SQL data and document context, choose "both".
5. Do not choose "analytics" unless an uploaded CSV/Excel dataset is available.

Reply with exactly one word:
sql, document, analytics, or both.
"""


class PlannerState(TypedDict):
    question: str
    route: str

    # Uploaded CSV/Excel data.
    dataframe: object | None

    sql_result: dict | None
    doc_result: dict | None
    analytics_result: dict | None
    final_answer: str


def route_question(state: PlannerState) -> PlannerState:
    """
    Determine which data source should handle the question.

    Routing considers:
    1. The user's question.
    2. Which data sources are actually available.
    3. Whether an uploaded dataset is available.

    The LLM remains responsible for semantic routing, while
    deterministic guards prevent an uploaded dataset from being
    ignored for questions that can clearly be answered from it.
    """

    question = state["question"]
    question_lower = question.lower()

    has_uploaded_dataset = (
        state.get("dataframe") is not None
    )

    metric_words = [
        "revenue",
        "sales",
        "units",
        "profit",
        "growth",
        "amount",
        "total",
        "average",
        "mean",
        "median",
        "maximum",
        "minimum",
        "highest",
        "lowest",
        "top",
        "bottom",
    ]

    reason_words = [
        "why",
        "reason",
        "cause",
        "root cause",
    ]

    analytics_words = [
        "dataset",
        "dataframe",
        "uploaded",
        "csv",
        "excel",
        "products",
        "columns",
        "correlation",
        "statistics",
        "statistical",
        "anomaly",
        "anomalies",
        "outlier",
        "outliers",
    ]

    document_words = [
        "report",
        "document",
        "pdf",
        "policy",
        "policies",
        "according to",
        "according to the report",
    ]

    has_metric = any(
        word in question_lower
        for word in metric_words
    )

    has_reason = any(
        word in question_lower
        for word in reason_words
    )

    has_analytics_signal = any(
        word in question_lower
        for word in analytics_words
    )

    has_document_signal = any(
        word in question_lower
        for word in document_words
    )

    # ---------------------------------------------------------
    # Uploaded dataset routing
    # ---------------------------------------------------------

    if has_uploaded_dataset:

        # Explicit document questions should still go
        # through the Document Agent.
        if has_document_signal and not has_metric:

            route = "document"

            logger.info(
                "Routed to document: document signal detected."
            )

        # Questions explicitly referring to the uploaded
        # dataset should use the Analytics Agent.
        elif has_analytics_signal:

            route = "analytics"

            logger.info(
                "Routed to analytics: uploaded dataset signal detected."
            )

        # Business metric questions can be answered directly
        # from the uploaded dataset.
        elif has_metric:

            route = "analytics"

            logger.info(
                "Routed to analytics: uploaded dataset available "
                "for business metric question."
            )

        else:

            # Let the LLM make the semantic decision for
            # questions that are not obviously analytical.
            routing_prompt = f"""
{ROUTER_SYSTEM_PROMPT}

IMPORTANT CONTEXT:

An uploaded CSV/Excel dataset IS available.

For this request, the Analytics Agent can directly analyze
the uploaded dataset using deterministic analytical tools.

Prefer "analytics" when the question can reasonably be
answered using the uploaded dataset.

Do NOT select "analytics" if the question specifically
requires information from a business document/report.

User question:
{question}
"""

            route = chat(
                routing_prompt,
                question,
            ).strip().lower()

    else:

        # -----------------------------------------------------
        # No uploaded dataset
        # -----------------------------------------------------

        if has_metric and has_reason:

            route = "both"

            logger.info(
                "Routed to both: metric + reason detected."
            )

        else:

            route = chat(
                ROUTER_SYSTEM_PROMPT,
                question,
            ).strip().lower()

    # ---------------------------------------------------------
    # Validate LLM output
    # ---------------------------------------------------------

    if route not in (
        "sql",
        "document",
        "analytics",
        "both",
    ):

        logger.warning(
            "Unexpected route '%s', defaulting to 'both'.",
            route,
        )

        route = "both"

    # ---------------------------------------------------------
    # Analytics requires an uploaded dataset
    # ---------------------------------------------------------

    if (
        route == "analytics"
        and not has_uploaded_dataset
    ):

        logger.warning(
            "Analytics route selected without uploaded "
            "dataset. Falling back to SQL."
        )

        route = "sql"

    logger.info(
        "Planner routing decision: %s",
        route,
    )

    state["route"] = route

    return state


def call_sql_agent(
    state: PlannerState,
) -> PlannerState:
    """
    Execute the SQL Agent.
    """

    with log_execution_time(
        logger,
        "SQL Agent",
    ):

        result = sql_answer(
            state["question"]
        )

        state["sql_result"] = {
            "explanation": result.explanation,
            "sql_query": result.sql_query,
        }

        return state


def call_document_agent(
    state: PlannerState,
) -> PlannerState:
    """
    Execute the Document/RAG Agent.
    """

    with log_execution_time(
        logger,
        "Document Agent",
    ):

        result = doc_answer(
            state["question"]
        )

        state["doc_result"] = {
            "answer": result.answer
        }

        return state


def call_data_analyst(
    state: PlannerState,
) -> PlannerState:
    """
    Run the Data Analyst Agent against
    the uploaded dataset.
    """

    with log_execution_time(
        logger,
        "Data Analyst Agent",
    ):

        dataframe = state.get("dataframe")

        if dataframe is None:

            logger.warning(
                "Analytics route selected but "
                "no dataset was provided."
            )

            state["analytics_result"] = {
                "error": (
                    "No CSV or Excel dataset "
                    "has been uploaded."
                )
            }

            return state

        result = analyze_dataset(
            dataframe,
            state["question"],
        )

        state["analytics_result"] = {
            "profile": result.profile,
            "analysis": result.analysis,
            "answer": result.answer,
            "chart": result.chart,
        }

        return state


def combine_answers(
    state: PlannerState,
) -> PlannerState:
    """
    Combine results from the selected agents.
    """

    with log_execution_time(
        logger,
        "Answer Combination",
    ):

        sql_part = state.get("sql_result")
        doc_part = state.get("doc_result")
        analytics_part = state.get(
            "analytics_result"
        )

        parts = []

        if sql_part:
            parts.append(
                f"SQL analysis:\n"
                f"{sql_part['explanation']}"
            )

        if doc_part:
            parts.append(
                f"Document analysis:\n"
                f"{doc_part['answer']}"
            )

        if analytics_part:

            if "error" in analytics_part:

                parts.append(
                    f"Analytics error:\n"
                    f"{analytics_part['error']}"
                )

            else:

                parts.append(
                    "Uploaded dataset analysis:\n"
                    f"{analytics_part['answer']}"
                )

        if not parts:

            state["final_answer"] = (
                "Could not generate an answer."
            )

            return state

        # If only one source produced a result,
        # return it directly without another LLM call.
        if len(parts) == 1:

            state["final_answer"] = (
                parts[0]
                .split("\n", 1)[-1]
            )

            return state

        prompt = (
            f"Question: {state['question']}\n\n"
            + "\n\n".join(parts)
            + """

Combine these findings into one clear,
evidence-based business answer.

Rules:
- Do not invent numbers.
- Do not contradict the supplied evidence.
- Merge overlapping findings.
- Clearly distinguish facts from interpretations.
- Keep the answer concise and business-friendly.
"""
        )

        state["final_answer"] = chat(
            "You are a senior business data analyst.",
            prompt,
        )

        return state


def decide_next(
    state: PlannerState,
) -> Literal[
    "sql",
    "document",
    "analytics",
    "both",
]:
    """
    Return the route selected by the planner.
    """

    return state["route"]


def build_graph():
    """
    Build and compile the LangGraph workflow.
    """

    graph = StateGraph(PlannerState)

    graph.add_node(
        "router",
        route_question,
    )

    graph.add_node(
        "sql_agent",
        call_sql_agent,
    )

    graph.add_node(
        "document_agent",
        call_document_agent,
    )

    graph.add_node(
        "data_analyst",
        call_data_analyst,
    )

    graph.add_node(
        "combine",
        combine_answers,
    )

    graph.set_entry_point("router")

    graph.add_conditional_edges(
        "router",
        decide_next,
        {
            "sql": "sql_agent",
            "document": "document_agent",
            "analytics": "data_analyst",
            "both": "sql_agent",
        },
    )

    # If the route is "both", execute SQL first
    # and then execute the Document Agent.
    graph.add_conditional_edges(
        "sql_agent",
        lambda state: (
            "document_agent"
            if state["route"] == "both"
            else "combine"
        ),
        {
            "document_agent": "document_agent",
            "combine": "combine",
        },
    )

    graph.add_edge(
        "document_agent",
        "combine",
    )

    graph.add_edge(
        "data_analyst",
        "combine",
    )

    graph.add_edge(
        "combine",
        END,
    )

    return graph.compile()


planner_graph = build_graph()

def analyze_with_details(
    question: str,
    dataframe=None,
) -> dict:
    """
    Run the Planner workflow and return the complete result.

    This is used by API clients that need access to
    analytics metadata such as generated visualizations.

    Unlike answer_question(), this function does not use
    the response cache because the complete workflow result
    may contain non-cacheable objects such as Plotly figures.
    """

    logger.info(
        "Running detailed analysis workflow."
    )

    result = planner_graph.invoke(
        {
            "question": question,
            "route": "",
            "dataframe": dataframe,
            "sql_result": None,
            "doc_result": None,
            "analytics_result": None,
            "final_answer": "",
        }
    )

    return result

def answer_question(
    question: str,
    dataframe=None,
) -> str:
    """
    Main entry point for the Planner workflow.

    Checks the dataset-aware cache first, then runs
    the LangGraph workflow when no cached answer exists.
    """

    cached = get_cached_answer(
        question,
        dataframe=dataframe,
    )

    if cached:

        logger.info(
            "Planner cache hit."
        )

        return cached

    logger.info(
        "Planner cache miss. "
        "Starting LangGraph workflow."
    )

    result = planner_graph.invoke(
        {
            "question": question,
            "route": "",
            "dataframe": dataframe,
            "sql_result": None,
            "doc_result": None,
            "analytics_result": None,
            "final_answer": "",
        }
    )

    answer = result["final_answer"]

    set_cached_answer(
        question,
        answer,
        dataframe=dataframe,
    )

    return answer