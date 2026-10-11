from __future__ import annotations

import runpy
from typing import Any, cast

import pytest

from aiplatform.mcp_server import server as server_module
from aiplatform.mcp_server.server import create_server
from aiplatform.mcp_server.tools import (
    get_control,
    score_waf_pillar,
    validate_evidence_filename,
)


async def test_fastmcp_dispatches_all_registered_tools() -> None:
    server = create_server()
    tool_names = sorted(tool.name for tool in await server.list_tools())

    assert tool_names == [
        "get_control",
        "list_module_b_controls",
        "score_waf_pillar",
        "validate_evidence_filename",
    ]

    _content, controls_payload = cast(
        tuple[list[Any], dict[str, list[dict[str, Any]]]],
        await server.call_tool("list_module_b_controls", {}),
    )
    _content, control = cast(
        tuple[list[Any], dict[str, Any]],
        await server.call_tool("get_control", {"ref": "B3.1"}),
    )
    _content, filename = cast(
        tuple[list[Any], dict[str, Any]],
        await server.call_tool(
            "validate_evidence_filename",
            {"name": "B3.1_DeploymentRunbook_v2.md"},
        ),
    )
    _content, score = cast(
        tuple[list[Any], dict[str, Any]],
        await server.call_tool(
            "score_waf_pillar",
            {"pillar": "ops", "answers": {"runbook": True}},
        ),
    )

    controls = controls_payload["result"]
    assert len(controls) == 7
    assert control["found"] is True
    assert control["ref"] == "B.3.1"
    assert filename["valid"] is True
    assert filename["control_ref"] == "B.3.1"
    assert score["pillar"] == "operations"
    assert score["missing_criteria"] == ["alerts", "deployment", "evals", "kt"]


def test_server_main_runs_stdio_transport(monkeypatch: pytest.MonkeyPatch) -> None:
    class NoopServer:
        def __init__(self) -> None:
            self.transport: str | None = None

        def run(self, *, transport: str) -> None:
            self.transport = transport

    noop_server = NoopServer()

    def fake_create_server() -> NoopServer:
        return noop_server

    monkeypatch.setattr(server_module, "create_server", fake_create_server)

    server_module.main()

    assert noop_server.transport == "stdio"


def test_package_main_entrypoint_delegates_to_server_main(monkeypatch: pytest.MonkeyPatch) -> None:
    called: list[bool] = []

    def fake_main() -> None:
        called.append(True)

    monkeypatch.setattr(server_module, "main", fake_main)

    runpy.run_module("aiplatform.mcp_server.__main__", run_name="__main__")

    assert called == [True]


def test_get_control_rejects_unknown_reference() -> None:
    result = get_control("B.9.9")

    assert result["found"] is False
    assert result["ref"] == "B.9.9"
    assert "B.3.1" in result["known_refs"]


def test_validate_evidence_filename_rejects_bad_shape() -> None:
    result = validate_evidence_filename("not evidence.txt")

    assert result == {
        "valid": False,
        "name": "not evidence.txt",
        "message": (
            "Use [ControlRef]_[DocumentType]_v[N].pdf, for example B.3.1_SolutionDesign_v1.pdf."
        ),
    }


def test_score_waf_pillar_rejects_unknown_pillar() -> None:
    result = score_waf_pillar("resilience", {})

    assert result["valid"] is False
    assert result["pillar"] == "resilience"
    assert result["known_pillars"] == [
        "cost",
        "operations",
        "performance",
        "reliability",
        "security",
    ]


@pytest.mark.parametrize(
    ("pillar", "answers", "expected_score", "expected_rating", "expected_recommendation"),
    [
        (
            "cost optimization",
            {
                "budget": "yes",
                "rightsize": "done",
                "tokens": 100,
                "shutdown": 1,
                "chargeback": "implemented",
            },
            100,
            "strong",
            "Ready to include in the Module B evidence pack.",
        ),
        (
            "performance-efficiency",
            {"sizing": 0.5, "autoscale": "partial", "latency": 50, "cache": 0, "load": 0},
            32,
            "high_risk",
            "Prioritise remediation before audit evidence sign-off.",
        ),
        (
            "reliability",
            {"slo": 0.8, "redundancy": 0.8, "dr": 0.7, "quota": 0.7, "testing": 0.8},
            76,
            "adequate",
            "Ready to include in the Module B evidence pack.",
        ),
        (
            "security",
            {"identity": True, "network": True, "data": False, "safety": False, "logging": False},
            45,
            "needs_remediation",
            "Prioritise remediation before audit evidence sign-off.",
        ),
    ],
)
def test_score_waf_pillar_ratings_and_recommendations(
    pillar: str,
    answers: dict[str, Any],
    expected_score: int,
    expected_rating: str,
    expected_recommendation: str,
) -> None:
    result = score_waf_pillar(pillar, answers)

    assert result["valid"] is True
    assert result["score"] == expected_score
    assert result["rating"] == expected_rating
    assert result["recommendation"] == expected_recommendation
    assert result["missing_criteria"] == []


def test_score_waf_pillar_clamps_numeric_and_unknown_string_answers() -> None:
    result = score_waf_pillar(
        "security",
        {"identity": 250, "network": -5, "data": "no", "safety": "in progress", "logging": True},
    )

    assert result["score"] == 50
    assert result["rating"] == "needs_remediation"
