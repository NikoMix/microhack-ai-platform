from __future__ import annotations

from collections.abc import AsyncIterator, Sequence

from aiplatform.agents.orchestrator import AgentOrchestrator
from aiplatform.agents.tools.base import AgentTool
from aiplatform.config import Settings
from aiplatform.inference import (
    BaseChatProvider,
    ChatResponse,
    EmbeddingResult,
    Message,
    ToolCall,
    ToolDefinition,
)


class ScriptedProvider(BaseChatProvider):
    provider_name = "scripted"

    def __init__(self) -> None:
        self.calls = 0
        self.closed = False

    async def complete(
        self,
        messages: Sequence[Message],
        *,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int | None = None,
        tools: Sequence[object] | None = None,
        response_format: dict[str, object] | None = None,
    ) -> ChatResponse:
        del model, temperature, max_tokens, tools, response_format
        self.calls += 1
        if self.calls == 1:
            return ChatResponse(
                content="Retrieving Module B context.",
                provider=self.provider_name,
                tool_calls=[
                    ToolCall(
                        id="call-1",
                        name="fake_retrieve",
                        arguments='{"query": "B.3.1 deployment", "k": 1}',
                    )
                ],
            )
        assert messages[-1].tool_call_id == "call-1"
        assert "B.3.1 deployment requires Azure AI Foundry" in messages[-1].content
        return ChatResponse(
            content="Use Azure AI Foundry for B.3.1 deployment evidence.",
            provider=self.provider_name,
        )

    async def stream(
        self,
        messages: Sequence[Message],
        *,
        model: str | None = None,
        temperature: float = 0.2,
        max_tokens: int | None = None,
    ) -> AsyncIterator[str]:
        del messages, model, temperature, max_tokens
        yield ""

    async def embed(self, texts: Sequence[str], *, model: str | None = None) -> EmbeddingResult:
        del texts, model
        return EmbeddingResult(vectors=[[0.0]], provider=self.provider_name)

    async def aclose(self) -> None:
        self.closed = True


async def test_orchestrator_runs_full_tool_calling_turn() -> None:
    provider = ScriptedProvider()

    async def fake_handler(arguments: dict[str, object], settings: Settings) -> dict[str, object]:
        del arguments, settings
        return {
            "chunks": [
                {
                    "text": "B.3.1 deployment requires Azure AI Foundry.",
                    "source": "module-b-controls",
                    "score": 1.0,
                }
            ]
        }

    tool = AgentTool(
        definition=ToolDefinition(name="fake_retrieve", description="fake", parameters={}),
        handler=fake_handler,
    )
    result = await AgentOrchestrator(
        Settings(),
        provider=provider,
        tools=[tool],
    ).run("What does B.3.1 require?")

    assert "Azure AI Foundry" in result.answer
    assert "Sources:" in result.answer
    assert result.citations == ["module-b-controls"]
    assert result.runtime == "local"
    assert provider.closed is False
