"""
Redis-based response caching.

Redis is treated as an optional infrastructure dependency.

The application must be able to start and operate even when
Redis is unavailable. Redis connections are therefore created
lazily when the cache is actually accessed rather than during
module import.
"""

import hashlib
import json

import redis

from app.utils.logger import get_logger


logger = get_logger(__name__)


CACHE_TTL_SECONDS = 60 * 60  # 1 hour

REDIS_HOST = "localhost"
REDIS_PORT = 6379

redis_client = None
REDIS_AVAILABLE = None


def _get_redis_client():
    """
    Lazily create and validate the Redis connection.

    Redis is not contacted during module import.

    Returns:
        Redis client if available.
        None if Redis is unavailable.
    """

    global redis_client
    global REDIS_AVAILABLE

    # Redis was already successfully initialized

    if REDIS_AVAILABLE is True:
        return redis_client

    # Redis was already determined to be unavailable
 
    if REDIS_AVAILABLE is False:
        return None

    # First Redis access: initialize connection
 
    try:

        client = redis.Redis(
            host=REDIS_HOST,
            port=REDIS_PORT,
            decode_responses=True,
            socket_connect_timeout=1,
            socket_timeout=1,
        )

        client.ping()

        redis_client = client
        REDIS_AVAILABLE = True

        logger.info(
            "Redis connection established successfully."
        )

        return redis_client

    except Exception as e:

        REDIS_AVAILABLE = False

        logger.warning(
            "Redis unavailable, caching disabled: %s",
            e,
        )

        return None


def _cache_key(question: str) -> str:
    """
    Generate a deterministic cache key from the question.
    """

    normalized = question.strip().lower()

    return (
        "qa:"
        + hashlib.sha256(
            normalized.encode()
        ).hexdigest()
    )


def get_cached_answer(
    question: str,
) -> str | None:
    """
    Retrieve an answer from Redis.

    Returns None when Redis is unavailable or
    the question is not cached.
    """

    client = _get_redis_client()

    if client is None:
        return None

    try:

        cached = client.get(
            _cache_key(question)
        )

        if cached:

            logger.info(
                "Cache hit - returning cached answer."
            )

            return json.loads(
                cached
            )["answer"]

    except Exception as e:

        logger.warning(
            "Cache read failed: %s",
            e,
        )

    return None


def set_cached_answer(
    question: str,
    answer: str,
) -> None:
    """
    Store an answer in Redis.

    Cache failures never interrupt the
    main application workflow.
    """

    client = _get_redis_client()

    if client is None:
        return

    try:

        client.setex(
            _cache_key(question),
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

    except Exception as e:

        logger.warning(
            "Cache write failed: %s",
            e,
        )