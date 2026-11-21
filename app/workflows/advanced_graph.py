
"""Phase 11: Advanced supervisor workflow using LangGraph."""

from collections.abc import Callable
from typing import Any

from langgraph.graph import END, START, StateGraph

from app.workflows.advanced_state import (
    ALLOWED_AGENTS,
    MAX_AGENT_EXECUTIONS,
    AdvancedPlannerState,
    route_to_plan,
)

from app.workflows.evidence_synthesis import (
    synthesize_advanced_answer,
)


# Each adapter receives the workflow state and returns a result.
AgentFunction = Callable[[AdvancedPlannerState], dict[str, Any]]


def build_advanced_graph(
    agents: dict[str, AgentFunction],
):
    """
    Build a bounded LangGraph supervisor.

    Existing V1 agents will be connected through adapters.
    """

    unknown = set(agents) - set(ALLOWED_AGENTS)

    if unknown:
        raise ValueError(f"Unsupported agents: {sorted(unknown)}")

    def plan_node(state: AdvancedPlannerState) -> dict:
        """Create an execution plan from the selected route."""

        route = state.get("route", "")
        dataframe = state.get("dataframe")

        plan = route_to_plan(
            route=route,
            has_dataframe=dataframe is not None,
        )

        return {
            "plan": plan,
            "current_index": 0,
            "execution_count": 0,
            "completed_steps": [],
            "failed_steps": [],
            "next_agent": "",
            "sql_result": None,
            "doc_result": None,
            "analytics_result": None,
            "final_answer": "",
            "workflow_status": "running",
        }

    def supervisor_node(state: AdvancedPlannerState) -> dict:
        """Decide which planned agent should execute next."""

        plan = state.get("plan", [])
        index = state.get("current_index", 0)
        count = state.get("execution_count", 0)

        if count >= MAX_AGENT_EXECUTIONS or index >= len(plan):
            return {"next_agent": "finish"}

        next_agent = plan[index]

        if next_agent not in agents:
            return {"next_agent": "unavailable"}

        return {"next_agent": next_agent}

    def dispatch(state: AdvancedPlannerState) -> str:
        """Select the next graph node."""

        next_agent = state.get("next_agent", "finish")

        if next_agent in agents:
            return "execute"

        if next_agent == "unavailable":
            return "unavailable"

        return "finalize"

    def execute_node(state: AdvancedPlannerState) -> dict:
        """Run exactly one planned agent."""

        agent_name = state["next_agent"]

        updates: dict[str, Any] = {
            "execution_count": state.get("execution_count", 0) + 1,
            "current_index": state.get("current_index", 0) + 1,
        }

        try:
            result = agents[agent_name](state)

            if not isinstance(result, dict):
                raise TypeError("Agent must return a dictionary")

            if not result:
                raise ValueError("Agent returned no result")

            result_field = {
                "sql": "sql_result",
                "document": "doc_result",
                "analytics": "analytics_result",
            }[agent_name]

            updates[result_field] = result
            updates["completed_steps"] = [
                *state.get("completed_steps", []),
                agent_name,
            ]

        except Exception:
            # Do not expose exception details to the user.
            updates["failed_steps"] = [
                *state.get("failed_steps", []),
                agent_name,
            ]

        return updates

    def unavailable_node(state: AdvancedPlannerState) -> dict:
        """Mark an unavailable planned agent as failed."""

        plan = state.get("plan", [])
        index = state.get("current_index", 0)
        agent_name = plan[index]

        return {
            "current_index": index + 1,
            "failed_steps": [
                *state.get("failed_steps", []),
                agent_name,
            ],
        }
    def finalize_node(state: AdvancedPlannerState) -> dict:
        """
        Finalize the advanced workflow using validated
        evidence from successful agents.
        """

        completed = state.get("completed_steps", [])
        failed = state.get("failed_steps", [])
        plan = state.get("plan", [])

        if not plan:
            return {
                "workflow_status": "invalid_plan",
                "final_answer": (
                    "No executable analysis plan was available."
                ),
                "next_agent": "finish",
            }

        if not completed:
            return {
                "workflow_status": "failed",
                "final_answer": (
                    "The requested analysis could not be "
                    "completed. Please try again."
                ),
                "next_agent": "finish",
            }

        status = (
            "partial_success"
            if failed
            else "success"
        )

        try:
            answer = synthesize_advanced_answer(state)

            if not answer.strip():
                raise ValueError(
                    "Evidence presenter returned no answer"
                )

        except Exception:
            return {
                "workflow_status": "failed",
                "final_answer": (
                    "Analysis results were produced, "
                    "but the final response could not "
                    "be generated."
                ),
                "next_agent": "finish",
            }

        return {
            "workflow_status": status,
            "final_answer": answer,
            "next_agent": "finish",
        }

    graph = StateGraph(AdvancedPlannerState)

    graph.add_node("plan", plan_node)
    graph.add_node("supervisor", supervisor_node)
    graph.add_node("execute", execute_node)
    graph.add_node("unavailable", unavailable_node)
    graph.add_node("finalize", finalize_node)

    graph.add_edge(START, "plan")
    graph.add_edge("plan", "supervisor")

    graph.add_conditional_edges(
        "supervisor",
        dispatch,
        {
            "execute": "execute",
            "unavailable": "unavailable",
            "finalize": "finalize",
        },
    )

    graph.add_edge("execute", "supervisor")
    graph.add_edge("unavailable", "supervisor")
    graph.add_edge("finalize", END)

    return graph.compile()
