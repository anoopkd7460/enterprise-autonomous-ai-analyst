
"""Phase 11: Shared state for advanced agent orchestration."""

from typing import Literal, TypedDict


# Supported agents in the existing project.
AgentName = Literal["sql", "document", "analytics"]

ALLOWED_AGENTS: tuple[AgentName, ...] = (
    "sql",
    "document",
    "analytics",
)

# Prevent unlimited agent execution.
MAX_AGENT_EXECUTIONS = 3


class AdvancedPlannerState(TypedDict, total=False):
    """Shared information used by the advanced workflow."""

    # User input
    question: str
    dataframe: object | None

    # Planning
    route: str
    plan: list[AgentName]
    next_agent: str

    # Execution tracking
    current_index: int
    execution_count: int

    # Workflow history
    completed_steps: list[AgentName]
    failed_steps: list[AgentName]

    # Error handling
    planner_error: bool

    # Results from existing agents
    sql_result: dict | None
    doc_result: dict | None
    analytics_result: dict | None

    # Final output
    final_answer: str
    workflow_status: str


def route_to_plan(
    route: str,
    has_dataframe: bool,
) -> list[AgentName]:
    """Convert the existing route into a safe execution plan."""

    mapping: dict[str, list[AgentName]] = {
        "sql": ["sql"],
        "document": ["document"],
        "analytics": ["analytics"],
        "both": ["sql", "document"],
    }

    plan = mapping.get(route, [])

    # Dataset analysis requires an uploaded dataset.
    if not has_dataframe and "analytics" in plan:
        return []

    # Enforce the execution limit.
    return plan[:MAX_AGENT_EXECUTIONS]
