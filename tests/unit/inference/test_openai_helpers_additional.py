from __future__ import annotations

from types import SimpleNamespace

from aiplatform.inference import Usage
from aiplatform.inference.providers._openai import (
    chat_response_from_openai,
    embedding_result_from_openai,
    usage_from_openai,
)


def test_usage_defaults_when_sdk_usage_is_missing() -> None:
    assert usage_from_openai(None) == Usage()


def test_chat_response_defaults_when_choices_are_missing() -> None:
    parsed = chat_response_from_openai(
        SimpleNamespace(choices=[]), provider="provider", fallback_model="fallback"
    )

    assert parsed.content == ""
    assert parsed.model == "fallback"
    assert parsed.provider == "provider"


def test_embedding_result_defaults_missing_data_and_model() -> None:
    parsed = embedding_result_from_openai(
        SimpleNamespace(data=None, usage=None), provider="provider", fallback_model="fallback"
    )

    assert parsed.vectors == []
    assert parsed.model == "fallback"
    assert parsed.usage.total_tokens == 0
