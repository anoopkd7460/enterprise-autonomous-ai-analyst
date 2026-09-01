"""
Redis-based response caching.

Redis is treated as an optional infrastructure dependency.

The application must be able to start and operate even when
Redis is unavailable. Redis connections are therefore created
lazily when the cache is actually accessed.

For uploaded CSV/Excel datasets, the cache key includes a
deterministic dataset fingerprint. This prevents an answer
generated for one dataset from being incorrectly returned
for another dataset with the same question.
"""

import hashlib
import json

import pandas as pd
import redis

from app.core.config import settings
from app.utils.logger import get_logger


logger = get_logger(__name__)


CACHE_TTL_SECONDS = 60 * 60  # 1 hour

redis_client = None
REDIS_AVAILABLE = None


def _get_redis_client():
    """
    Lazily create and validate the Redis connection.

    Redis is only contacted when caching is enabled.

    Returns:
        Redis client if available.
        None if Redis is disabled or unavailable.
    """

    global redis_client
    global REDIS_AVAILABLE

    # ---------------------------------------------------------
    # Redis explicitly disabled
    # ---------------------------------------------------------

    if not settings.REDIS_ENABLED:

        REDIS_AVAILABLE = False

        return None

    # ---------------------------------------------------------
    # Redis already initialized successfully
    # ---------------------------------------------------------

    if REDIS_AVAILABLE is True:
        return redis_client

    # ---------------------------------------------------------
    # Redis already determined to be unavailable
    # ---------------------------------------------------------

    if REDIS_AVAILABLE is False:
        return None

    # ---------------------------------------------------------
    # First Redis access
    # ---------------------------------------------------------

    try:

        client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            decode_responses=True,
            socket_connect_timeout=(
                settings.REDIS_CONNECT_TIMEOUT
            ),
            socket_timeout=(
                settings.REDIS_SOCKET_TIMEOUT
            ),
        )

        client.ping()

        redis_client = client
        REDIS_AVAILABLE = True

        logger.info(
            "Redis connection established successfully."
        )

        return redis_client

    except Exception as exc:

        REDIS_AVAILABLE = False

        logger.warning(
            "Redis unavailable, caching disabled: %s",
            exc,
        )

        return None


def _dataset_hash(
    dataframe,
) -> str | None:
    """
    Generate a deterministic fingerprint for a Pandas DataFrame.

    The fingerprint changes when dataset content, columns,
    or data types change.

    Returns:
        SHA-256 dataset fingerprint, or None when no valid
        DataFrame is provided.
    """

    if dataframe is None:
        return None

    try:

        if not isinstance(
            dataframe,
            pd.DataFrame,
        ):
            return None

        # Hash DataFrame values and index.
        row_hash = pd.util.hash_pandas_object(
            dataframe,
            index=True,
        )

        # Include column names and data types.
        metadata = (
            str(list(dataframe.columns))
            + str(
                list(
                    dataframe.dtypes.astype(str)
                )
            )
        )

        payload = (
            row_hash.values.tobytes()
            + metadata.encode()
        )

        return hashlib.sha256(
            payload
        ).hexdigest()

    except Exception as exc:

        logger.warning(
            "Could not generate dataset fingerprint: %s",
            exc,
        )

        return None


def _cache_key(
    question: str,
    dataset_hash: str | None = None,
) -> str:
    """
    Generate a deterministic cache key.

    The question is always part of the key.

    When a dataset is provided, its fingerprint is also
    included so that answers are isolated per dataset.
    """

    normalized_question = (
        question.strip().lower()
    )

    cache_input = normalized_question

    if dataset_hash:
        cache_input += (
            f":dataset:{dataset_hash}"
        )

    return (
        "qa:"
        + hashlib.sha256(
            cache_input.encode()
        ).hexdigest()
    )


def get_cached_answer(
    question: str,
    dataframe=None,
) -> str | None:
    """
    Retrieve an answer from Redis.

    Returns:
        Cached answer if available.
        None when Redis is disabled, unavailable,
        or no cached answer exists.
    """

    client = _get_redis_client()

    if client is None:

        return None

    try:

        dataset_hash = _dataset_hash(
            dataframe
        )

        cached = client.get(
            _cache_key(
                question,
                dataset_hash,
            )
        )

        if cached:

            logger.info(
                "Cache hit - returning cached answer."
            )

            return json.loads(
                cached
            )["answer"]

        logger.info(
            "Cache miss - no cached answer found."
        )

    except Exception as exc:

        logger.warning(
            "Cache read failed: %s",
            exc,
        )

    return None


def set_cached_answer(
    question: str,
    answer: str,
    dataframe=None,
) -> None:
    """
    Store an answer in Redis.

    Cache failures never interrupt the main
    application workflow.
    """

    client = _get_redis_client()

    if client is None:
        return

    try:

        dataset_hash = _dataset_hash(
            dataframe
        )

        client.setex(
            _cache_key(
                question,
                dataset_hash,
            ),
            CACHE_TTL_SECONDS,
            json.dumps(
                {
                    "answer": answer
                }
            ),
        )

        logger.info(
            "Answer cached successfully."
        )

    except Exception as exc:

        logger.warning(
            "Cache write failed: %s",
            exc,
        )