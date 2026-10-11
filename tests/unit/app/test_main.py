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


class FakeRetriever:
    async def retrieve(self, query: str, k: int = 4) -> list[Any]:
        return [
            RetrievedChunk(
                text="Contoso expenses need receipts for lodging.",
                source="expenses.md",
                score=0.9,
            )
        ]


class FakeProvider(BaseChatProvider):
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
        assert "expenses.md" in messages[-1].content
        return ChatResponse(
            content="Receipts are required for lodging.", provider="fake", model="m"
        )

    async def stream(
        self,
        messages: Sequence[Message],
        *,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        yield "delta"

    async def embed(self, texts: Sequence[str], *, model: str | None = None) -> EmbeddingResult:
        return EmbeddingResult(vectors=[[1.0]])


async def test_healthz_and_chat(monkeypatch: Any) -> None:
    monkeypatch.setattr("aiplatform.app.main.get_retriever", lambda settings: FakeRetriever())
    monkeypatch.setattr("aiplatform.app.main.get_chat_provider", lambda settings: FakeProvider())
    app = create_app(Settings())

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        health = await client.get("/healthz")
        chat = await client.post("/api/chat", json={"message": "What needs receipts?"})

    assert health.json()["status"] == "ok"
    assert chat.status_code == 200
    assert chat.json()["citations"] == ["expenses.md"]
    assert "Receipts are required" in chat.json()["answer"]
