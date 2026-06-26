from __future__ import annotations

import sys
import types
from collections.abc import AsyncIterator, Sequence
from dataclasses import dataclass
from typing import Any

import pytest

from aiplatform.agents import orchestrator as orchestrator_module
from aiplatform.agents.orchestrator import (
    AgentOrchestrator,
    _extract_citations,
    _latest_text_message,
    run_agent,
)
from aiplatform.agents.tools.base import AgentTool
from aiplatform.config import InferenceProvider, Settings
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

    def __init__(self, responses: Sequence[ChatResponse]) -> None:
        self._responses = list(responses)
        self.seen_messages: list[list[Message]] = []
        self.seen_tools: list[list[str]] = []
        self.closed = False

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
        del model, temperature, max_tokens, response_format
        self.seen_messages.append(list(messages))
        self.seen_tools.append([tool.name for tool in tools or []])
        if not self._responses:
            raise AssertionError("ScriptedProvider received an unexpected completion call")
        return self._responses.pop(0)

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


@dataclass(frozen=True, slots=True)
class FoundryText:
    value: str


@dataclass(frozen=True, slots=True)
class FoundryContent:
    text: FoundryText


@dataclass(frozen=True, slots=True)
class FoundryMessage:
    role: str
    content: list[FoundryContent]


async def test_orchestrator_executes_tool_turn_and_aggregates_citations() -> None:
    provider = ScriptedProvider(
        [
            ChatResponse(
                content="Need evidence.",
                tool_calls=[
                    ToolCall(
                        id="call-1",
                        name="fake_retrieve",
                        arguments='{"query": "B.3.1 deployment"}',
                    )
                ],
            ),
            ChatResponse(content="Azure AI Foundry deployment evidence is required."),
        ]
    )

    async def fake_handler(arguments: dict[str, Any], settings: Settings) -> dict[str, Any]:
        assert arguments == {"query": "B.3.1 deployment"}
        assert isinstance(settings, Settings)
        return {
            "chunks": [
                {"text": "Deploy with Foundry.", "source": "module-b-controls", "score": 1.0},
                {"text": "Review WAF.", "source": "waf-notes", "score": 0.8},
            ],
            "citations": [{"source": "module-b-controls"}, "extra-citation"],
        }

    tool = AgentTool(
        definition=ToolDefinition(name="fake_retrieve", description="fake", parameters={}),
        handler=fake_handler,
    )

    result = await AgentOrchestrator(Settings(), provider=provider, tools=[tool], max_turns=3).run(
        "What evidence is needed?"
    )

    assert result.runtime == "local"
    assert result.rai_flags == []
    assert result.citations == [
        "module-b-controls",
        "waf-notes",
        "module-b-controls",
        "extra-citation",
    ]
    assert "Sources:" in result.answer
    assert "[1] module-b-controls" in result.answer
    assert "[2] waf-notes" in result.answer
    assert "[3] extra-citation" in result.answer
    assert provider.seen_tools == [["fake_retrieve"], ["fake_retrieve"]]
    assert provider.seen_messages[1][-1].tool_call_id == "call-1"
    assert "Deploy with Foundry" in provider.seen_messages[1][-1].content
    assert provider.closed is False


async def test_orchestrator_returns_turn_limit_fallback_with_rai_flags() -> None:
    provider = ScriptedProvider(
        [
            ChatResponse(
                content="Still searching.",
                tool_calls=[
                    ToolCall(
                        id="call-limit",
                        name="fake_retrieve",
                        arguments='{"query": "anything"}',
                    )
                ],
            )
        ]
    )

    async def fake_handler(arguments: dict[str, Any], settings: Settings) -> dict[str, Any]:
        del arguments, settings
        return {"chunks": [{"text": "context", "source": "limit-source", "score": 0.5}]}

    result = await AgentOrchestrator(
        Settings(),
        provider=provider,
        tools=[
            AgentTool(
                definition=ToolDefinition(name="fake_retrieve", description="fake"),
                handler=fake_handler,
            )
        ],
        max_turns=1,
    ).run("Loop forever?")

    assert "turn limit" in result.answer
    assert "Sources:" in result.answer
    assert result.citations == ["limit-source"]
    assert result.rai_flags == ["missing_platform_context"]


async def test_execute_tool_handles_unknown_bad_json_and_non_object_arguments() -> None:
    async def unused_handler(arguments: dict[str, Any], settings: Settings) -> dict[str, Any]:
        del arguments, settings
        raise AssertionError("handler should not run for invalid arguments")

    orchestrator = AgentOrchestrator(
        Settings(),
        provider=ScriptedProvider([]),
        tools=[
            AgentTool(
                definition=ToolDefinition(name="known_tool", description="known"),
                handler=unused_handler,
            )
        ],
    )

    unknown = await orchestrator._execute_tool(ToolCall(id="1", name="missing_tool"))
    invalid_json = await orchestrator._execute_tool(
        ToolCall(id="2", name="known_tool", arguments="{")
    )
    non_object = await orchestrator._execute_tool(
        ToolCall(id="3", name="known_tool", arguments='["not", "an", "object"]')
    )

    assert unknown == {"error": "Unknown tool: missing_tool"}
    assert invalid_json["error"] == "invalid_json_arguments"
    assert non_object == {"error": "arguments_must_be_object"}


async def test_run_agent_owns_and_closes_default_provider(monkeypatch: pytest.MonkeyPatch) -> None:
    provider = ScriptedProvider([ChatResponse(content="Azure answer with no tool calls.")])

    def fake_get_chat_provider(settings: Settings) -> BaseChatProvider:
        assert isinstance(settings, Settings)
        return provider

    monkeypatch.setattr(orchestrator_module, "get_chat_provider", fake_get_chat_provider)

    result = await run_agent("hello", Settings())

    assert result.answer == "Azure answer with no tool calls."
    assert result.runtime == "local"
    assert provider.closed is True


async def test_optional_agent_framework_runtime_falls_back_to_local(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    del monkeypatch
    provider = ScriptedProvider([ChatResponse(content="Azure local fallback.")])
    result = await AgentOrchestrator(Settings(), provider=provider, runtime="agent_framework").run(
        "question"
    )

    assert result.runtime == "local"
    assert result.answer == "Azure local fallback."


async def test_agent_framework_detected_without_adapter_returns_none(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(sys.modules, "agent_framework", types.ModuleType("agent_framework"))
    result = await AgentOrchestrator(
        Settings(), provider=ScriptedProvider([])
    )._run_agent_framework("question")

    assert result is None


async def test_run_returns_agent_framework_result_when_adapter_supplies_one(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_framework(
        self: AgentOrchestrator, question: str
    ) -> orchestrator_module.AgentResult:
        del self
        assert question == "question"
        return orchestrator_module.AgentResult(answer="framework answer", runtime="agent_framework")

    monkeypatch.setattr(AgentOrchestrator, "_run_agent_framework", fake_framework)

    result = await AgentOrchestrator(
        Settings(), provider=ScriptedProvider([]), runtime="agent_framework"
    ).run("question")

    assert result.answer == "framework answer"
    assert result.runtime == "agent_framework"


async def test_foundry_runtime_import_guard_falls_back_to_local(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = Settings(
        inference_provider=InferenceProvider.AZURE_AI_FOUNDRY,
        azure_ai_foundry_project_endpoint="https://example.invalid",
        azure_ai_foundry_agent_id="agent-id",
    )
    provider = ScriptedProvider([ChatResponse(content="Azure local fallback.")])

    def missing_import(name: str) -> types.ModuleType:
        del name
        raise ImportError("optional sdk missing")

    monkeypatch.setattr(orchestrator_module, "import_module", missing_import)

    result = await AgentOrchestrator(settings, provider=provider, runtime="foundry").run("question")

    assert result.runtime == "local"
    assert result.answer == "Azure local fallback."


async def test_run_returns_foundry_result_when_configured(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = Settings(
        inference_provider=InferenceProvider.AZURE_AI_FOUNDRY,
        azure_ai_foundry_project_endpoint="https://example.invalid",
        azure_ai_foundry_agent_id="agent-id",
    )

    async def fake_foundry(
        self: AgentOrchestrator, question: str
    ) -> orchestrator_module.AgentResult:
        del self
        assert question == "question"
        return orchestrator_module.AgentResult(answer="foundry answer", runtime="foundry")

    monkeypatch.setattr(AgentOrchestrator, "_run_foundry_agent", fake_foundry)

    result = await AgentOrchestrator(
        settings, provider=ScriptedProvider([]), runtime="foundry"
    ).run("question")

    assert result.answer == "foundry answer"
    assert result.runtime == "foundry"


async def test_foundry_runtime_success_extracts_latest_assistant_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    settings = Settings(
        inference_provider=InferenceProvider.AZURE_AI_FOUNDRY,
        azure_ai_foundry_project_endpoint="https://example.invalid",
        azure_ai_foundry_agent_id="agent-id",
    )

    class FakeThreads:
        def create(self) -> types.SimpleNamespace:
            return types.SimpleNamespace(id="thread-1")

    class FakeMessages:
        def create(self, *, thread_id: str, role: str, content: str) -> None:
            assert (thread_id, role, content) == ("thread-1", "user", "question")

        def list(self, *, thread_id: str) -> list[FoundryMessage]:
            assert thread_id == "thread-1"
            return [
                FoundryMessage(role="user", content=[]),
                FoundryMessage(
                    role="assistant",
                    content=[FoundryContent(text=FoundryText(value="Foundry answer"))],
                ),
            ]

    class FakeRuns:
        def create_and_process(self, *, thread_id: str, agent_id: str) -> types.SimpleNamespace:
            assert (thread_id, agent_id) == ("thread-1", "agent-id")
            return types.SimpleNamespace(status="completed")

    class FakeAgents:
        def __init__(self) -> None:
            self.threads = FakeThreads()
            self.messages = FakeMessages()
            self.runs = FakeRuns()

    class FakeAIProjectClient:
        def __init__(self, *, endpoint: str, credential: object) -> None:
            assert endpoint == "https://example.invalid"
            assert credential is not None
            self.agents = FakeAgents()

    class FakeDefaultAzureCredential:
        pass

    projects_module = types.ModuleType("azure.ai.projects")
    projects_module.__dict__["AIProjectClient"] = FakeAIProjectClient
    identity_module = types.ModuleType("azure.identity")
    identity_module.__dict__["DefaultAzureCredential"] = FakeDefaultAzureCredential

    def fake_import_module(name: str) -> types.ModuleType:
        if name == "azure.ai.projects":
            return projects_module
        if name == "azure.identity":
            return identity_module
        raise ImportError(name)

    monkeypatch.setattr(orchestrator_module, "import_module", fake_import_module)

    result = await AgentOrchestrator(settings, provider=ScriptedProvider([]))._run_foundry_agent(
        "question"
    )

    assert result is not None
    assert result.answer == "Foundry answer"
    assert result.runtime == "foundry"


async def test_final_self_check_reports_invalid_flag_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_self_check(arguments: dict[str, Any], settings: Settings) -> dict[str, Any]:
        assert arguments["answer"] == "Azure answer"
        assert isinstance(settings, Settings)
        return {"flags": "not-a-list"}

    monkeypatch.setattr(orchestrator_module, "responsible_ai_self_check", fake_self_check)

    flags = await AgentOrchestrator(
        Settings(), provider=ScriptedProvider([])
    )._run_final_self_check("Azure answer", [])

    assert flags == ["invalid_rai_check_payload"]


def test_extract_citations_ignores_malformed_items() -> None:
    assert _extract_citations(
        {
            "chunks": [{"source": "chunk-source"}, "bad", {"source": "  "}],
            "citations": [{"source": "citation-source"}, " inline-source ", 3],
        }
    ) == ["chunk-source", "citation-source", "inline-source"]


def test_latest_text_message_returns_empty_when_no_assistant_text() -> None:
    assert _latest_text_message([FoundryMessage(role="user", content=[])]) == ""
