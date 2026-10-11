from __future__ import annotations

import os

import pytest

from aiplatform.config import Settings
from aiplatform.inference import Message, get_chat_provider


@pytest.mark.integration
@pytest.mark.asyncio
async def test_live_github_models_smoke() -> None:
    if not os.environ.get("GITHUB_TOKEN"):
        pytest.skip("GITHUB_TOKEN is required for live GitHub Models smoke test")
    provider = get_chat_provider(Settings(github_token=os.environ["GITHUB_TOKEN"]))
    try:
        response = await provider.complete([Message.user("Reply with one word: ok")], max_tokens=5)
    finally:
        await provider.aclose()
    assert response.content
