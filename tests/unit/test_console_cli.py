"""Unit tests for the top-level ``aiplatform`` console CLI.

These exercise the command dispatch and graceful-failure behaviour without any
network access: the inference provider and retriever are replaced with stubs.
"""

from __future__ import annotations

import sys
from typing import Any

import pytest

from aiplatform import cli
from aiplatform.inference.base import ChatResponse, ProviderError
from aiplatform.rag.types import RetrievedChunk


class _FakeRetriever:
    """Retriever stub returning canned chunks (no embeddings/network)."""

    def __init__(self, chunks: list[RetrievedChunk]) -> None:
        self._chunks = chunks

    async def retrieve(self, query: str, k: int = 4) -> list[RetrievedChunk]:
        del query, k
        return self._chunks


class _FakeProvider:
    """Chat provider stub that either returns a response or raises."""

    def __init__(
        self, *, response: ChatResponse | None = None, error: ProviderError | None = None
    ) -> None:
        self._response = response
        self._error = error
        self.closed = False

    async def complete(self, messages: Any, **kwargs: Any) -> ChatResponse:
        del messages, kwargs
        if self._error is not None:
            raise self._error
        assert self._response is not None
        return self._response

    async def aclose(self) -> None:
        self.closed = True


def test_providers_command_renders_table(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "argv", ["aiplatform", "providers"])

    cli.main()

    output = capsys.readouterr().out
    assert "github_models" in output


def test_no_command_prints_help(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "argv", ["aiplatform"])

    cli.main()

    output = capsys.readouterr().out
    assert "Contoso AI Assistant CLI" in output


def test_chat_handles_provider_error_gracefully(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    provider = _FakeProvider(
        error=ProviderError("GitHub Models chat completion failed", provider="github_models")
    )
    retriever = _FakeRetriever([])
    monkeypatch.setattr(cli, "get_chat_provider", lambda settings: provider)
    monkeypatch.setattr(cli, "get_retriever", lambda settings: retriever)
    monkeypatch.setattr(sys, "argv", ["aiplatform", "chat", "What does B.3.1 require?"])

    with pytest.raises(SystemExit) as excinfo:
        cli.main()

    assert excinfo.value.code == 2
    output = capsys.readouterr().out
    assert "GITHUB_TOKEN" in output
    # The provider must still be closed via the finally block even on error.
    assert provider.closed is True


def test_chat_prints_answer_and_sources(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    chunks = [RetrievedChunk(text="Body text", source="doc-a", score=1.0)]
    provider = _FakeProvider(response=ChatResponse(content="Answer body", provider="fake"))
    monkeypatch.setattr(cli, "get_chat_provider", lambda settings: provider)
    monkeypatch.setattr(cli, "get_retriever", lambda settings: _FakeRetriever(chunks))
    monkeypatch.setattr(sys, "argv", ["aiplatform", "--verbose", "chat", "hello"])

    cli.main()

    output = capsys.readouterr().out
    assert "Answer body" in output
    assert "doc-a" in output
    assert provider.closed is True


def test_ingest_reports_document_count(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    async def _fake_ingest(settings: Any) -> int:
        del settings
        return 7

    monkeypatch.setattr(cli, "ingest", _fake_ingest)
    monkeypatch.setattr(sys, "argv", ["aiplatform", "ingest"])

    cli.main()

    output = capsys.readouterr().out
    assert "Indexed 7 documents" in output
