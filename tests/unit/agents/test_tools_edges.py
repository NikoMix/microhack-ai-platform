from __future__ import annotations

import pytest

from aiplatform.agents.tools import default_tools
from aiplatform.agents.tools.citation_formatter import (
    citation_formatter_tool,
    format_cited_answer,
)
from aiplatform.agents.tools.rai_self_check import (
    responsible_ai_self_check,
    responsible_ai_self_check_tool,
)
from aiplatform.agents.tools.retrieval import retrieval_tool, retrieve_knowledge
from aiplatform.config import Settings
from aiplatform.rag import RetrievedChunk


class RecordingRetriever:
    def __init__(self) -> None:
        self.requests: list[tuple[str, int]] = []

    async def retrieve(self, query: str, k: int = 4) -> list[RetrievedChunk]:
        self.requests.append((query, k))
        return [RetrievedChunk(text=f"chunk for {query}", source="recorded.md", score=0.7)]


def test_default_tools_exposes_expected_tool_names() -> None:
    tools = default_tools()
    assert [tool.definition.name for tool in tools] == [
        "retrieve_knowledge",
        "format_cited_answer",
        "responsible_ai_self_check",
    ]


def test_tool_factories_wire_handlers_and_schema() -> None:
    retrieval = retrieval_tool()
    formatter = citation_formatter_tool()
    rai = responsible_ai_self_check_tool()

    assert retrieval.handler is retrieve_knowledge
    assert retrieval.definition.parameters["required"] == ["query"]
    assert formatter.handler is format_cited_answer
    assert formatter.definition.parameters["required"] == ["answer", "citations"]
    assert rai.handler is responsible_ai_self_check
    assert rai.definition.parameters["required"] == ["answer"]


async def test_retrieve_knowledge_returns_warning_for_empty_query(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_get_retriever(settings: Settings) -> RecordingRetriever:
        del settings
        raise AssertionError("empty queries should not create a retriever")

    monkeypatch.setattr("aiplatform.agents.tools.retrieval.get_retriever", fail_get_retriever)

    result = await retrieve_knowledge({"query": "   ", "k": 3}, Settings())

    assert result == {"chunks": [], "warning": "query was empty"}


async def test_retrieve_knowledge_defaults_bool_and_invalid_k(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    retrievers: list[RecordingRetriever] = []

    def fake_get_retriever(settings: Settings) -> RecordingRetriever:
        assert isinstance(settings, Settings)
        retriever = RecordingRetriever()
        retrievers.append(retriever)
        return retriever

    monkeypatch.setattr("aiplatform.agents.tools.retrieval.get_retriever", fake_get_retriever)

    bool_result = await retrieve_knowledge({"query": "azure", "k": True}, Settings())
    invalid_result = await retrieve_knowledge({"query": "github", "k": object()}, Settings())

    assert retrievers[0].requests == [("azure", 4)]
    assert retrievers[1].requests == [("github", 4)]
    assert bool_result["chunks"][0]["source"] == "recorded.md"
    assert invalid_result["chunks"][0]["text"] == "chunk for github"


async def test_retrieve_knowledge_clamps_numeric_k(monkeypatch: pytest.MonkeyPatch) -> None:
    retriever = RecordingRetriever()

    def fake_get_retriever(settings: Settings) -> RecordingRetriever:
        del settings
        return retriever

    monkeypatch.setattr("aiplatform.agents.tools.retrieval.get_retriever", fake_get_retriever)

    await retrieve_knowledge({"query": "low", "k": -10}, Settings())
    await retrieve_knowledge({"query": "high", "k": 99}, Settings())

    assert retriever.requests == [("low", 1), ("high", 8)]


async def test_format_cited_answer_handles_non_list_and_non_dict_citations() -> None:
    non_list = await format_cited_answer(
        {"answer": "Azure answer", "citations": "oops"}, Settings()
    )
    mixed = await format_cited_answer(
        {
            "answer": "GitHub answer",
            "citations": ["skip", {"source": " source.md ", "quote": " quote "}],
        },
        Settings(),
    )

    assert non_list == {"answer": "Azure answer", "citations": []}
    assert mixed["citations"] == [{"source": "source.md", "quote": "quote"}]
    assert "source.md — quote" in mixed["answer"]


async def test_responsible_ai_self_check_flags_empty_and_unsafe_answers() -> None:
    empty = await responsible_ai_self_check({"answer": "", "citations": []}, Settings())
    unsafe = await responsible_ai_self_check(
        {"answer": "Disable security logging in Azure.", "citations": ["control.md"]},
        Settings(),
    )

    assert empty["flags"] == ["empty_answer", "missing_citations", "missing_platform_context"]
    assert unsafe == {"passed": False, "flags": ["potentially_unsafe_guidance"]}
