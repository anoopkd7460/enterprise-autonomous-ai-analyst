from pydantic import BaseModel, Field

class AnalyzeRequest(BaseModel):
    """Request body for the AI analyst."""

    question: str = Field(
        ...,
        min_length=3,
        description="Natural-language business question."
    )

class AnalyzeResponse(BaseModel):
    """Response returned by the AI analyst."""

    question: str
    answer: str


class HealthResponse(BaseModel):
    """Health-check response."""

    status: str
    service: str