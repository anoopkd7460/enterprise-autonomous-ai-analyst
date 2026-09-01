"""
FastAPI application entry point.

The API exposes the Enterprise Autonomous AI Analyst
through HTTP endpoints.
"""

import time
import uuid

from fastapi import FastAPI, Request
from app.api.routes import router
from app.utils.logger import get_logger

logger = get_logger(__name__)


app = FastAPI(
    title = "Enterprise Autonomous AI Analyst",
    description=(
        "AI-powered business analystics platform "
        "using LangGraph, LangChain, SQL, RAG, "
        "and deterministic analytics."
    ),
    version="1.0.0",
)


@app.middleware("http")
async def observability_middleware(
    request: Request,
    call_next,
):
    """
    Add request-level observability.

    Each HTTP request receives:
    - A unique request ID.
    - Request execution timing.
    - Start and completion logs.
    """

    request_id = str(uuid.uuid4())

    start_time = time.perf_counter()

    # Make request ID available to downstream code.
    request.state.request_id = request_id

    logger.info(
        "[%s] Request started: %s %s",
        request_id,
        request.method,
        request.url.path,
    )

    try:

        response = await call_next(request)

        elapsed_time = (
            time.perf_counter() - start_time
        )

        response.headers[
            "X-Request-ID"
        ] = request_id

        logger.info(
            "[%s] Request completed: "
            "status=%d latency=%.3fs",
            request_id,
            response.status_code,
            elapsed_time,
        )

        return response

    except Exception:

        elapsed_time = (
            time.perf_counter() - start_time
        )

        logger.exception(
            "[%s] Request failed: latency=%.3fs",
            request_id,
            elapsed_time,
        )

        raise


app.include_router(router)


@app.get("/")
def root():
    """
    Basic service health endpoint.
    """

    return {
        "service": (
            "Enterprise Autonomous AI Analyst"
        ),
        "status": "running",
        "docs": "/docs",
    }