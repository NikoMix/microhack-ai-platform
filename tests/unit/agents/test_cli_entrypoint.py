from __future__ import annotations

import runpy
import sys

import pytest

from aiplatform.agents import orchestrator as orchestrator_module
from aiplatform.agents.orchestrator import AgentResult
from aiplatform.config import Settings


class EntrypointOrchestrator:
    def __init__(self, settings: Settings, *, runtime: str = "local") -> None:
        assert isinstance(settings, Settings)
        assert runtime == "local"

    async def run(self, question: str) -> AgentResult:
        assert question == "entrypoint question"
        return AgentResult(answer="Entrypoint Azure answer", runtime="local")


def test_agents_module_entrypoint_invokes_main(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(orchestrator_module, "AgentOrchestrator", EntrypointOrchestrator)
    monkeypatch.setattr(sys, "argv", ["aiplatform-agents", "entrypoint question"])

    # Evict the already-imported module so runpy executes it fresh without the
    # "found in sys.modules ... prior to execution" RuntimeWarning. monkeypatch
    # restores the original entry after the test.
    monkeypatch.delitem(sys.modules, "aiplatform.agents.__main__", raising=False)
    runpy.run_module("aiplatform.agents.__main__", run_name="__main__")

    assert "Entrypoint Azure answer" in capsys.readouterr().out
