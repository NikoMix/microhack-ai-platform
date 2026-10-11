from __future__ import annotations

from collections.abc import AsyncIterator, Sequence
from importlib import import_module
from typing import Any

from httpx import ASGITransport, AsyncClient

from aiplatform.config import Settings
from aiplatform.inference import (
    BaseChatProvider,
    ChatResponse,
    EmbeddingResult,
    Message,
    ToolDefinition,
)


def _aiplatform_module(*parts: str) -> Any:
    return import_module(".".join(("aiplatform", *parts)))


create_app = _aiplatform_module("app", "main").create_app
RetrievedChunk = _aiplatform_module("rag", "types").RetrievedChunk


class EmptyRetriever:
    def __init__(self) -> None:
        self.queries: list[str] = []

    async def retrieve(self, query: str, k: int = 4) -> list[Any]:
        self.queries.append(query)
        return []


class StreamingProvider(BaseChatProvider):
    provider_name = "streaming"

    def __init__(self) -> None:
        self.closed = False
        self.completed_messages: list[list[Message]] = []

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
        self.completed_messages.append(list(messages))
        return ChatResponse(content="No context answer.", provider="streaming", model="model-a")

    async def stream(
        self,
        messages: Sequence[Message],
        *,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        yield "first"
        yield "second"

    async def embed(self, texts: Sequence[str], *, model: str | None = None) -> EmbeddingResult:
        return EmbeddingResult(vectors=[[1.0] for _ in texts])

    async def aclose(self) -> None:
        self.closed = True


class RaisingProvider(StreamingProvider):
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
        raise RuntimeError("guardrail blocked")


async def test_index_chat_messages_prompt_no_citations_and_stream(
    monkeypatch: Any,
) -> None:
    retriever = EmptyRetriever()
    provider = StreamingProvider()

    monkeypatch.setattr("aiplatform.app.main.get_retriever", lambda settings: retriever)
    monkeypatch.setattr("aiplatform.app.main.get_chat_provider", lambda settings: provider)
    app = create_app(Settings())

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        index = await client.get("/")
        chat = await client.post(
            "/api/chat",
            json={
                "messages": [
                    {"role": "system", "content": "Be concise."},
                    {"role": "user", "content": "Earlier question"},
                    {"role": "assistant", "content": "Earlier answer"},
                    {"role": "tool", "content": "Ignored tool content"},
                    {"role": "user", "content": "Latest question"},
                ]
            },
        )
        stream = await client.get("/api/stream", params={"message": "Stream this"})

    assert index.status_code == 200
    assert "Contoso AI Assistant" in index.text
    assert retriever.queries == ["Latest question", "Stream this"]
    assert chat.json()["answer"] == "No context answer."
    assert chat.json()["citations"] == []
    assert "No context retrieved." in provider.completed_messages[0][-1].content
    assert [message.role.value for message in provider.completed_messages[0][1:-1]] == [
        "system",
        "user",
        "assistant",
    ]
    assert '"delta": "first"' in stream.text
    assert "data: [DONE]" in stream.text
    assert provider.closed


async def test_chat_provider_exception_returns_500_and_closes_provider(
    monkeypatch: Any,
) -> None:
    retriever = EmptyRetriever()
    provider = RaisingProvider()

    monkeypatch.setattr("aiplatform.app.main.get_retriever", lambda settings: retriever)
    monkeypatch.setattr("aiplatform.app.main.get_chat_provider", lambda settings: provider)
    app = create_app(Settings())

    async with AsyncClient(
        transport=ASGITransport(app=app, raise_app_exceptions=False),
        base_url="http://test",
    ) as client:
        response = await client.post("/api/chat", json={})

    assert response.status_code == 500
    assert provider.closed
    assert retriever.queries == [""]
