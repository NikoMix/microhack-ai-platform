"""Provider-agnostic tool-calling orchestrator for the MicroHack agentic layer."""

from __future__ import annotations

import json
import logging
from collections.abc import Sequence
from dataclasses import dataclass, field
from importlib import import_module
from typing import Any, Literal

from aiplatform.agents.tools import AgentTool, default_tools
from aiplatform.agents.tools.rai_self_check import responsible_ai_self_check
from aiplatform.config import InferenceProvider, Settings, get_settings
from aiplatform.inference import BaseChatProvider, Message, Role, ToolCall, get_chat_provider

LOGGER = logging.getLogger(__name__)
RuntimeName = Literal["local", "foundry", "agent_framework"]

SYSTEM_PROMPT = """You are Contoso AI Assistant, the Module B lab coach for a 1-day
Train-the-Trainer MicroHack on the AI Platform on Microsoft Azure Specialization.
Use tools for retrieval and self-checks. Ground Azure guidance in cited sources.
Prefer zero-cost GitHub Models compatible tool calling unless an Azure AI Foundry
Agent Service runtime is explicitly configured. Explain modular inference, MCP,
GitHub Copilot custom agents, Responsible AI, and Azure AI Foundry in practical
lab language. Do not invent control requirements; retrieve before answering."""


@dataclass(frozen=True, slots=True)
class AgentResult:
    """Final output from an orchestrator run."""

    answer: str
    citations: list[str] = field(default_factory=list)
    rai_flags: list[str] = field(default_factory=list)
    runtime: str = "local"


class AgentOrchestrator:
    """Run a provider-agnostic local tool-calling agent loop."""

    def __init__(
        self,
        settings: Settings | None = None,
        *,
        provider: BaseChatProvider | None = None,
        tools: Sequence[AgentTool] | None = None,
        max_turns: int = 6,
        runtime: RuntimeName = "local",
    ) -> None:
        """Create an orchestrator.

        Args:
            settings: Runtime configuration.
            provider: Optional provider injection for tests.
            tools: Local tools to advertise to the model.
            max_turns: Maximum provider turns before returning the best answer.
            runtime: ``local`` by default, or optional Azure/Agent Framework paths.
        """
        self._settings = settings or get_settings()
        self._provider = provider
        self._owns_provider = provider is None
        self._tools = {tool.definition.name: tool for tool in (tools or default_tools())}
        self._max_turns = max(1, max_turns)
        self._runtime = runtime

    async def run(self, question: str) -> AgentResult:
        """Answer ``question`` with local tools or a guarded optional runtime."""
        if self._runtime == "agent_framework":
            framework_result = await self._run_agent_framework(question)
            if framework_result is not None:
                return framework_result
        if self._runtime == "foundry" and self._foundry_configured():
            foundry_result = await self._run_foundry_agent(question)
            if foundry_result is not None:
                return foundry_result
        return await self._run_local(question)

    async def _run_local(self, question: str) -> AgentResult:
        """Run the provider contract tool-calling loop."""
        provider = self._provider or get_chat_provider(self._settings)
        citations: list[str] = []
        messages: list[Message] = [Message.system(SYSTEM_PROMPT), Message.user(question)]
        try:
            for _turn in range(self._max_turns):
                response = await provider.complete(
                    messages,
                    tools=[tool.definition for tool in self._tools.values()],
                )
                if not response.requested_tool_calls:
                    answer = self._ensure_citations(response.content, citations)
                    rai_flags = await self._run_final_self_check(answer, citations)
                    return AgentResult(
                        answer=answer,
                        citations=citations,
                        rai_flags=rai_flags,
                        runtime="local",
                    )
                messages.append(
                    Message(
                        role=Role.ASSISTANT,
                        content=response.content,
                        tool_calls=response.tool_calls,
                    )
                )
                for tool_call in response.tool_calls:
                    payload = await self._execute_tool(tool_call)
                    citations.extend(_extract_citations(payload))
                    messages.append(
                        Message(
                            role=Role.TOOL,
                            content=json.dumps(payload, ensure_ascii=False),
                            name=tool_call.name,
                            tool_call_id=tool_call.id,
                        )
                    )
            fallback = self._ensure_citations(
                "I reached the local agent turn limit before producing a complete answer.",
                citations,
            )
            rai_flags = await self._run_final_self_check(fallback, citations)
            return AgentResult(
                answer=fallback, citations=citations, rai_flags=rai_flags, runtime="local"
            )
        finally:
            if self._owns_provider:
                await provider.aclose()

    async def _execute_tool(self, tool_call: ToolCall) -> dict[str, Any]:
        """Execute a requested local tool and return a serialisable payload."""
        tool = self._tools.get(tool_call.name)
        if tool is None:
            LOGGER.warning("Unknown tool requested", extra={"tool_name": tool_call.name})
            return {"error": f"Unknown tool: {tool_call.name}"}
        try:
            arguments = json.loads(tool_call.arguments or "{}")
        except json.JSONDecodeError as exc:
            LOGGER.warning("Invalid tool arguments", extra={"tool_name": tool_call.name})
            return {"error": "invalid_json_arguments", "detail": str(exc)}
        if not isinstance(arguments, dict):
            return {"error": "arguments_must_be_object"}
        LOGGER.info("Executing agent tool", extra={"tool_name": tool_call.name})
        return await tool.handler(arguments, self._settings)

    def _foundry_configured(self) -> bool:
        """Return whether the optional Azure AI Foundry Agent Service path is configured."""
        return (
            self._settings.inference_provider == InferenceProvider.AZURE_AI_FOUNDRY
            and bool(self._settings.azure_ai_foundry_project_endpoint)
            and bool(self._settings.azure_ai_foundry_agent_id)
        )

    async def _run_foundry_agent(self, question: str) -> AgentResult | None:
        """Run the optional Azure AI Foundry Agent Service path when installed.

        The SDK is imported only inside this guarded path so the default GitHub
        Models/local tool-calling flow remains dependency-light and zero-cost.
        """
        try:
            projects_module = import_module("azure.ai.projects")
            identity_module = import_module("azure.identity")
        except ImportError:
            LOGGER.info("Azure AI Foundry SDK not installed; falling back to local runtime")
            return None
        try:
            client = projects_module.AIProjectClient(
                endpoint=self._settings.azure_ai_foundry_project_endpoint,
                credential=identity_module.DefaultAzureCredential(),
            )
            agents_client = client.agents
            thread = agents_client.threads.create()
            agents_client.messages.create(thread_id=thread.id, role="user", content=question)
            run = agents_client.runs.create_and_process(
                thread_id=thread.id,
                agent_id=self._settings.azure_ai_foundry_agent_id,
            )
            if getattr(run, "status", "") == "failed":
                LOGGER.warning("Foundry agent run failed; falling back to local runtime")
                return None
            messages = agents_client.messages.list(thread_id=thread.id)
            answer = _latest_text_message(messages)
            if not answer:
                return None
            return AgentResult(answer=answer, runtime="foundry")
        except Exception:
            LOGGER.exception("Foundry agent runtime failed; falling back to local runtime")
            return None

    async def _run_agent_framework(self, question: str) -> AgentResult | None:
        """Gracefully detect the optional Microsoft Agent Framework path."""
        del question
        try:
            __import__("agent_framework")
        except ImportError:
            LOGGER.info("Microsoft Agent Framework is not installed; using local runtime")
            return None
        LOGGER.info("Microsoft Agent Framework detected but no lab adapter is configured")
        return None

    async def _run_final_self_check(self, answer: str, citations: Sequence[str]) -> list[str]:
        """Run the deterministic Responsible AI check on the final answer."""
        payload = await responsible_ai_self_check(
            {"answer": answer, "citations": list(citations)},
            self._settings,
        )
        flags = payload.get("flags", [])
        if isinstance(flags, list):
            return [str(flag) for flag in flags]
        return ["invalid_rai_check_payload"]

    def _ensure_citations(self, answer: str, citations: Sequence[str]) -> str:
        """Append citations when the model omitted an explicit source block."""
        clean_answer = answer.strip()
        if not citations or "sources:" in clean_answer.lower():
            return clean_answer
        lines = [
            f"[{index}] {source}" for index, source in enumerate(dict.fromkeys(citations), start=1)
        ]
        return f"{clean_answer}\n\nSources:\n" + "\n".join(lines)


async def run_agent(question: str, settings: Settings | None = None) -> AgentResult:
    """Convenience helper for running the default local orchestrator."""
    orchestrator = AgentOrchestrator(settings)
    return await orchestrator.run(question)


def _extract_citations(payload: dict[str, Any]) -> list[str]:
    """Extract source names from tool payloads."""
    citations: list[str] = []
    chunks = payload.get("chunks", [])
    if isinstance(chunks, list):
        for item in chunks:
            if isinstance(item, dict):
                source = str(item.get("source", "")).strip()
                if source:
                    citations.append(source)
    formatted = payload.get("citations", [])
    if isinstance(formatted, list):
        for item in formatted:
            if isinstance(item, dict):
                source = str(item.get("source", "")).strip()
                if source:
                    citations.append(source)
            elif isinstance(item, str) and item.strip():
                citations.append(item.strip())
    return citations


def _latest_text_message(messages: Any) -> str:
    """Best-effort extraction of the latest assistant text from Foundry messages."""
    for message in messages:
        if getattr(message, "role", "") != "assistant":
            continue
        content_items = getattr(message, "content", [])
        for item in content_items:
            text = getattr(getattr(item, "text", None), "value", "")
            if text:
                return str(text)
    return ""
