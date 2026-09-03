from unittest.mock import Mock

import pandas as pd

from app.services import cache_service


def sample_dataframe():
    return pd.DataFrame(
        {
            "product": [
                "Laptop",
                "Mobile",
                "Laptop",
            ],
            "revenue": [
                1000,
                500,
                1500,
            ],
        }
    )


def test_cache_key_same_question():
    key_1 = cache_service._cache_key(
        "What are the top products?"
    )

    key_2 = cache_service._cache_key(
        "What are the top products?"
    )

    assert key_1 == key_2


def test_cache_key_normalizes_question():
    key_1 = cache_service._cache_key(
        "What are the top products?"
    )

    key_2 = cache_service._cache_key(
        "  WHAT ARE THE TOP PRODUCTS?  "
    )

    assert key_1 == key_2


def test_cache_key_different_questions():
    key_1 = cache_service._cache_key(
        "What are the top products?"
    )

    key_2 = cache_service._cache_key(
        "What is total revenue?"
    )

    assert key_1 != key_2


def test_dataset_hash_same_dataset():
    df = sample_dataframe()

    hash_1 = cache_service._dataset_hash(df)
    hash_2 = cache_service._dataset_hash(df.copy())

    assert hash_1 == hash_2


def test_dataset_hash_different_dataset():
    df_1 = sample_dataframe()

    df_2 = sample_dataframe()
    df_2.loc[0, "revenue"] = 9999

    hash_1 = cache_service._dataset_hash(df_1)
    hash_2 = cache_service._dataset_hash(df_2)

    assert hash_1 != hash_2


def test_dataset_hash_includes_structure():
    df_1 = sample_dataframe()

    df_2 = df_1.copy()
    df_2["region"] = [
        "North",
        "South",
        "West",
    ]

    hash_1 = cache_service._dataset_hash(df_1)
    hash_2 = cache_service._dataset_hash(df_2)

    assert hash_1 != hash_2


def test_same_question_same_dataset_same_cache_key():
    df = sample_dataframe()

    dataset_hash = cache_service._dataset_hash(df)

    key_1 = cache_service._cache_key(
        "What are the top products?",
        dataset_hash,
    )

    key_2 = cache_service._cache_key(
        "What are the top products?",
        dataset_hash,
    )

    assert key_1 == key_2


def test_same_question_different_dataset_different_cache_key():
    df_1 = sample_dataframe()

    df_2 = sample_dataframe()
    df_2.loc[0, "revenue"] = 9999

    hash_1 = cache_service._dataset_hash(df_1)
    hash_2 = cache_service._dataset_hash(df_2)

    key_1 = cache_service._cache_key(
        "What are the top products?",
        hash_1,
    )

    key_2 = cache_service._cache_key(
        "What are the top products?",
        hash_2,
    )

    assert key_1 != key_2


def test_question_without_dataset():
    key = cache_service._cache_key(
        "What is total revenue?"
    )

    assert key.startswith("qa:")
    assert len(key) == 67


def test_dataset_hash_none_without_dataset():
    result = cache_service._dataset_hash(None)

    assert result is None

def test_get_cached_answer_when_redis_unavailable(monkeypatch):
    monkeypatch.setattr(
        cache_service,
        "_get_redis_client",
        lambda: None,
    )

    result = cache_service.get_cached_answer(
        "What are the top products?"
    )

    assert result is None


def test_set_cached_answer_when_redis_write_fails(monkeypatch):
    fake_client = Mock()

    fake_client.setex.side_effect = RuntimeError(
        "Redis connection lost"
    )

    monkeypatch.setattr(
        cache_service,
        "_get_redis_client",
        lambda: fake_client,
    )

    cache_service.set_cached_answer(
        "What are the top products?",
        "Laptop generated the highest revenue.",
    )

    fake_client.setex.assert_called_once()