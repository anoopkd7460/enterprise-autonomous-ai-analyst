"""
FastAPI backend exposing the Planner Agent over HTTP.
This lets any client (web, mobile, another service) call the agent
without needing direct Python access to this codebase.
"""

from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.analytics.data_loader import (
    SUPPORTED_EXTENSIONS,
    load_dataset,
)
from app.api.schemas import (
    AnalyzeResponse,
    HealthResponse,
)
from app.utils.logger import get_logger
from app.workflows.graph import answer_question


logger = get_logger(__name__)


router = APIRouter(
    prefix="/api/v1",
    tags=["AI Analyst"],
)


@router.get(
    "/health",
    response_model=HealthResponse,
)
def health_check() -> HealthResponse:
    """Check whether the API service is running."""

    return HealthResponse(
        status="healthy",
        service="enterprise-autonomous-ai-analyst",
    )


@router.post(
    "/analyze",
    response_model=AnalyzeResponse,
)
def analyze(
    question: str = Form(..., min_length=3),
    file: UploadFile | None = File(None),
) -> AnalyzeResponse:
    """
    Analyze a business question.

    A CSV/Excel file can optionally be uploaded.
    If a file is provided, it is loaded into a DataFrame
    and passed to the LangGraph workflow.
    """

    temporary_file = None

    try:

        logger.info(
            "Received analysis request: %s",
            question,
        )

        dataframe = None

        # -------------------------------------------------
        # Optional dataset processing
        # -------------------------------------------------

        if file is not None:

            filename = file.filename or ""

            extension = Path(filename).suffix.lower()

            if extension not in SUPPORTED_EXTENSIONS:
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Unsupported file type: {extension}. "
                        f"Supported types: "
                        f"{sorted(SUPPORTED_EXTENSIONS)}"
                    ),
                )

            logger.info(
                "Dataset upload received: %s",
                filename,
            )

            # Save upload temporarily so the existing
            # data_loader can process it.
            temporary_file = NamedTemporaryFile(
                delete=False,
                suffix=extension,
            )

            content = file.file.read()

            temporary_file.write(content)
            temporary_file.close()

            dataframe = load_dataset(
                temporary_file.name
            )

            logger.info(
                "Uploaded dataset loaded: rows=%d columns=%d",
                len(dataframe),
                len(dataframe.columns),
            )

        # -------------------------------------------------
        # Run existing AI workflow
        # -------------------------------------------------

        answer = answer_question(
            question,
            dataframe=dataframe,
        )

        return AnalyzeResponse(
            question=question,
            answer=answer,
        )

    except HTTPException:
        raise

    except FileNotFoundError as exc:

        logger.exception(
            "Uploaded dataset could not be found."
        )

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except ValueError as exc:

        logger.exception(
            "Invalid dataset."
        )

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        logger.exception(
            "Analysis request failed."
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Unable to process the analysis request."
            ),
        ) from exc

    finally:

        # Clean up temporary file.
        if temporary_file is not None:

            try:
                Path(
                    temporary_file.name
                ).unlink(
                    missing_ok=True
                )

            except Exception:

                logger.warning(
                    "Failed to remove temporary file: %s",
                    temporary_file.name,
                )