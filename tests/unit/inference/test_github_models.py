from __future__ import annotations

import pytest
import respx
from httpx import Response

from aiplatform.config import Settings
from aiplatform.inference import Message, ProviderError
from aiplatform.inference.providers.github_models import GitHubModelsProvider


@pytest.mark.asyncio
@respx.mock
async def test_github_models_complete_and_embed() -> None:
    settings = Settings()
    provider = GitHubModelsProvider(settings)
    respx.post("https://models.github.ai/inference/chat/completions").mock(
        return_value=Response(
            200,
            json={
                "id": "chatcmpl-1",
                "object": "chat.completion",
                "created": 1,
                "model": "gpt-4o-mini",
                "choices": [
                    {
                        "index": 0,
                        "message": {"role": "assistant", "content": "Hello from Contoso"},
                        "finish_reason": "stop",
                    }
                ],
                "usage": {"prompt_tokens": 1, "completion_tokens": 2, "total_tokens": 3},
            },
        )
    )
    respx.post("https://models.github.ai/inference/embeddings").mock(
        return_value=Response(
            200,
            json={
                "object": "list",
                "model": "text-embedding-3-small",
                "data": [{"object": "embedding", "index": 0, "embedding": [1.0, 0.0]}],
                "usage": {"prompt_tokens": 1, "total_tokens": 1},
            },
        )
    )

    completion = await provider.complete([Message.user("Hi")])
    embeddings = await provider.embed(["Hi"])
    await provider.aclose()

    assert completion.content == "Hello from Contoso"
    assert completion.provider == "github_models"
    assert embeddings.vectors == [[1.0, 0.0]]


@pytest.mark.asyncio
@respx.mock
async def test_github_models_wraps_errors() -> None:
    provider = GitHubModelsProvider(Settings())
    respx.post("https://models.github.ai/inference/chat/completions").mock(
        return_value=Response(400, json={"error": {"message": "bad"}})
    )

    with pytest.raises(ProviderError) as exc_info:
        await provider.complete([Message.user("Hi")])
    await provider.aclose()

    assert exc_info.value.provider == "github_models"
