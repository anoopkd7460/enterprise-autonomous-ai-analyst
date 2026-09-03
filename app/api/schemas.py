from pydantic import BaseModel, Field
from typing import Any

class AnalyzeRequest(BaseModel):
    """Request body for the AI analyst."""

    question: str = Field(
        ...,
        min_length=3,
        description="Natural-language business question."
    )

class DatasetMetadata(BaseModel):
    """Metadata describing the analyzed dataset."""

    filename: str | None = None
    rows: int | None = None
    columns: int | None = None
    numeric_columns: int | None = None
    missing_values: int | None = None

class AnalyzeResponse(BaseModel):
    """Response returned by the AI analyst."""

    question: str
    answer: str
    chart: dict[str, Any] | None = None
    dataset_metadata: DatasetMetadata | None = None

class HealthResponse(BaseModel):
    """Health-check response."""

    status: str
    service: str