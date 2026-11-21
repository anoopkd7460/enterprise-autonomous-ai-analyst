
# Phase 11 — Advanced Agentic Workflows

## Project
Enterprise Autonomous AI Analyst

## Objective

Enhance the existing LangGraph-based AI Analyst with
controlled agent orchestration, execution tracking,
failure recovery, and evidence-aware answers.

## Previous Architecture — Portfolio V1

User Question
    |
Planner / Router
    |
SQL / Document RAG / Dataset Analytics
    |
Answer Combiner
    |
Final Answer

## Phase 11 Architecture

User Question
    |
Existing V1 Router
    |
Advanced Supervisor
    |
Execution Plan
    |
Agent Dispatcher
    |
SQL / Document / Analytics Agent
    |
Evidence Validation
    |
Supervisor (next step or finish)
    |
Deterministic Evidence Presenter
    |
Final Answer

## Implemented Features

### 1. Advanced Workflow State

File: app/workflows/advanced_state.py

Responsibilities:
- Define supported agents
- Convert routes into execution plans
- Track execution status
- Limit agent executions

### 2. Advanced Supervisor

File: app/workflows/advanced_graph.py

Responsibilities:
- Manage sequential task execution
- Dispatch tasks to registered agents
- Track completed and failed steps
- Prevent unbounded execution
- Support partial-success outcomes

### 3. Existing Agent Integration

File: app/workflows/agent_adapters.py

Reuses the existing SQL, Document RAG,
and Dataset Analytics Agents.

Additional validation:
- Empty SQL results
- NULL-only SQL results
- Missing document evidence
- Invalid agent responses
- Selected hardcoded SQL evidence claims

### 4. Evidence-Aware Presentation

File: app/workflows/evidence_synthesis.py

Responsibilities:
- Preserve executed SQL queries and results
- Display retrieved document excerpts
- Distinguish AI interpretations from evidence
- Disclose incomplete analysis
- Avoid an additional synthesis LLM call

### 5. Reporting-Year Clarification

Questions mentioning a specific quarter without
an explicit four-digit year request clarification.

Examples:
- Q4 -> Clarification required
- Q4 2024 -> Normal workflow

Limitations:
- Fiscal-year shorthand is not supported
- Relative date expressions are not fully handled

### 6. Feature Flag

Environment variable:

ADVANCED_WORKFLOW_ENABLED=false

Default: false

When disabled:
- The existing Portfolio V1 workflow is used.

When enabled:
- The Phase 11 advanced workflow is used.
- Advanced workflow responses bypass the V1
  response cache.

## Testing

Portfolio V1 baseline: 70 tests

Phase 11 additions: 30 tests

Total reported passing: 100 tests

Test categories:
- Supervisor orchestration
- SQL and document evidence validation
- Partial and complete agent failures
- Dataset routing
- Execution limits
- Reporting-year clarification
- Deterministic answer presentation
- SQL evidence provenance checks

## Known Limitations

- Successful execution does not prove factual accuracy.
- SQL provenance validation is intentionally narrow.
- Retrieval quality is not independently scored.
- Original agent explanations can contain unsupported
  business interpretations.
- Date clarification does not cover every date format.
- Advanced workflow performance has not been
  load-tested.
- AWS deployment is not part of Phase 11.

## Portfolio V1 Protection

- Development uses a separate Git feature branch.
- The advanced workflow is disabled by default.
- The original agent implementation remains available.
- No production deployment is required for this phase.

## Completion Criteria

- All automated tests pass.
- Existing V1 behavior remains compatible.
- Advanced workflow compiles successfully.
- Feature flag selects the correct workflow.
- Git formatting checks pass.
- Changes are reviewed and committed.
