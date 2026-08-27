"""
Redis-based response caching. If the same question was asked recently, return the cached instantly of re-running the full agent pipeline (multiple LLM calls + SQL + retrieval)
"""

import hashlib
import json

import redis

from app.utils.logger import get_logger

logger = get_logger(__name__)

CACHE_TTL_SECONDS = 60 * 60 # 1 hours

try:
    redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)
    redis_client.ping()
    REDIS_AVAILABLE = True
except Exception as e:
    logger.warning(f"Redis not available, caching disabled: {e}")
    REDIS_AVAILABLE = False


def _cache_key(question: str) -> str:
    # Hash the question so cache keys are short and consistent regardless of casing/spacing
    normalized = question.strip().lower()
    return "qa:" + hashlib.sha256(normalized.encode()).hexdigest()


def get_cached_answer(question: str) -> str | None:
    if not REDIS_AVAILABLE:
        return None
    try:
        cached = redis_client.get(_cache_key(question))
        if cached:
            logger.info("Cache hit - returning cached answer.")
            return json.loads(cached)["answer"]
    except Exception as e:
        logger.warning(f"Cache read failed: {e}")
    return None


def set_cached_answer(question: str, answer: str):
    if not REDIS_AVAILABLE:
        return
    try:
        redis_client.setex(
            _cache_key(question),
            CACHE_TTL_SECONDS,
            json.dumps({"answer": answer}),
        )
    except Exception as e:
        logger.warning(f"Cache write failed: {e}")