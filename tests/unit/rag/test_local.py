from __future__ import annotations

import importlib
from collections.abc import AsyncIterator, Sequence
from typing import Any

from aiplatform.config import Settings
from aiplatform.inference import (
    BaseChatProvider,
    ChatResponse,
    EmbeddingResult,
    Message,
    ToolDefinition,
)

local_module: Any = importlib.import_module(".".join(["aiplatform", "rag", "local"]))
LocalRetriever = local_module.LocalRetriever
load_corpus = local_module.load_corpus


class FakeEmbeddingProvider(BaseChatProvider):
    provider_name = "fake"

    async def complete(
        self,
        messages: Sequence[Message],
        *,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int | None = None,
        tools: Sequence[ToolDefinition] | None = None,
        response_format: dict[str, Any] | None = None,
    ) -> ChatResponse:
        return ChatResponse(content="unused", provider=self.provider_name)

    async def stream(
        self,
        messages: Sequence[Message],
        *,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        if False:
            yield ""

    async def embed(self, texts: Sequence[str], *, model: str | None = None) -> EmbeddingResult:
        vectors = [_vector_for(text) for text in texts]
        return EmbeddingResult(vectors=vectors, provider=self.provider_name)


def _vector_for(text: str) -> list[float]:
    lower = text.lower()
    return [
        1.0 if "expense" in lower or "receipt" in lower else 0.0,
        1.0 if "security" in lower or "access" in lower else 0.0,
        0.1,
    ]


async def test_local_retriever_ranks_relevant_chunk(monkeypatch: Any) -> None:
    monkeypatch.setattr(
        "aiplatform.rag.local.get_chat_provider", lambda settings: FakeEmbeddingProvider()
    )
    retriever = LocalRetriever(Settings())

    chunks = await retriever.retrieve("How do expense receipts work?", k=2)

    assert chunks[0].source == "expenses.md"
    assert chunks[0].score > chunks[1].score


def test_load_corpus_contains_contoso_snippets() -> None:
    corpus = load_corpus()

    assert len(corpus) >= 6
    assert any(document.source == "ai-platform.md" for document in corpus)
