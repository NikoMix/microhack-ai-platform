from __future__ import annotations

import sys

import pytest

from aiplatform.agents import __main__ as cli
from aiplatform.agents.orchestrator import AgentResult
from aiplatform.config import Settings
from aiplatform.inference.base import ProviderError


class _RaisingOrchestrator:
    """Stub orchestrator whose run raises ProviderError (no credentials)."""

    def __init__(self, settings: Settings, *, runtime: str = "local") -> None:
        del settings, runtime

    async def run(self, question: str) -> AgentResult:
        del question
        raise ProviderError("GitHub Models chat completion failed", provider="github_models")


class _OkOrchestrator:
    """Stub orchestrator returning a deterministic answer with an RAI flag."""

    def __init__(self, settings: Settings, *, runtime: str = "local") -> None:
        del settings, runtime

    async def run(self, question: str) -> AgentResult:
        del question
        return AgentResult(
            answer="Hello from Contoso",
            citations=["module-b-controls"],
            rai_flags=["pii_detected"],
            runtime="local",
        )


def test_cli_handles_provider_error_gracefully(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(cli, "AgentOrchestrator", _RaisingOrchestrator)
    monkeypatch.setattr(sys, "argv", ["aiplatform-agents", "What does B.3.1 require?"])

    with pytest.raises(SystemExit) as excinfo:
        cli.main()

    assert excinfo.value.code == 2
    output = capsys.readouterr().out
    assert "GITHUB_TOKEN" in output


def test_cli_prints_answer_and_rai_flags(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(cli, "AgentOrchestrator", _OkOrchestrator)
    monkeypatch.setattr(sys, "argv", ["aiplatform-agents", "hello"])

    cli.main()

    output = capsys.readouterr().out
    assert "Hello from Contoso" in output
    assert "Responsible AI flags" in output
