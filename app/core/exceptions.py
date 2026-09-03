"""
Application-specific exceptions.

These exceptions allow the API layer to distinguish between
expected application failures and unexpected programming errors.
"""


class ApplicationError(Exception):
    """Base exception for expected application failures."""

    def __init__(
        self,
        message: str,
    ) -> None:
        self.message = message
        super().__init__(message)


class AIServiceError(ApplicationError):
    """
    Raised when an AI/LLM service cannot complete a request.
    """

    pass


class AnalysisTimeoutError(ApplicationError):
    """
    Raised when analysis exceeds the allowed processing time.
    """

    pass