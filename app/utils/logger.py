"""
Shared application logger.

Provides consistent logging configuration and
execution-time measurement across the application.
"""

import logging
import sys
import time
from contextlib import contextmanager
from typing import Iterator


LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)s | "
    "%(name)s | "
    "%(message)s"
)


logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ],
)


def get_logger(name: str) -> logging.Logger:
    """
    Return a module-specific logger.

    Args:
        name: Logger name, normally __name__.

    Returns:
        Configured logging.Logger instance.
    """

    return logging.getLogger(name)


@contextmanager
def log_execution_time(
    logger: logging.Logger,
    operation: str,
) -> Iterator[None]:
    """
    Measure and log the execution time of an operation.

    Args:
        logger: Logger used to record the timing.
        operation: Human-readable operation name.

    Example:
        with log_execution_time(logger, "SQL Agent"):
            run_sql_agent()
    """

    start_time = time.perf_counter()

    try:
        yield

    finally:
        elapsed_time = (
            time.perf_counter() - start_time
        )

        logger.info(
            "%s completed | latency=%.3fs",
            operation,
            elapsed_time,
        )