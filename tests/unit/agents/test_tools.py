from __future__ import annotations

import pytest

from aiplatform.agents.tools.citation_formatter import format_cited_answer
from aiplatform.agents.tools.rai_self_check import responsible_ai_self_check
from aiplatform.agents.tools.retrieval import retrieve_knowledge
from aiplatform.config import Settings
from aiplatform.rag import RetrievedChunk


class StubRetriever:
    async def retrieve(self, query: str, k: int = 4) -> list[RetrievedChunk]:
        assert query == "agentic layer"
        assert k == 2
        return [RetrievedChunk(text="MCP helps agents use tools.", source="stub.md", score=0.9)]


@pytest.mark.asyncio
async def test_retrieval_tool_uses_configured_retriever(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get_retriever(settings: Settings) -> StubRetriever:
        assert isinstance(settings, Settings)
        return StubRetriever()

    monkeypatch.setattr("aiplatform.agents.tools.retrieval.get_retriever", fake_get_retriever)
    result = await retrieve_knowledge({"query": "agentic layer", "k": 2}, Settings())
    assert result["chunks"] == [
        {"text": "MCP helps agents use tools.", "source": "stub.md", "score": 0.9}
    ]


@pytest.mark.asyncio
async def test_formatter_deduplicates_sources() -> None:
    result = await format_cited_answer(
        {
            "answer": "Azure AI Foundry supports production migration.",
            "citations": [
                {"source": "a.md"},
                {"source": "a.md"},
                {"source": "b.md", "quote": "quote"},
            ],
        },
        Settings(),
    )
    assert result["answer"].count("a.md") == 1
    assert "b.md — quote" in result["answer"]


@pytest.mark.asyncio
async def test_responsible_ai_self_check_flags_missing_citations() -> None:
    result = await responsible_ai_self_check({"answer": "A generic answer."}, Settings())
    assert result["passed"] is False
    assert "missing_citations" in result["flags"]
    assert "missing_platform_context" in result["flags"]
