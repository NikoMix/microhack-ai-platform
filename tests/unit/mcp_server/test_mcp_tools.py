from __future__ import annotations

from aiplatform.mcp_server.server import create_server
from aiplatform.mcp_server.tools import (
    get_control,
    list_module_b_controls,
    score_waf_pillar,
    validate_evidence_filename,
)


def test_list_module_b_controls_contains_seven_controls() -> None:
    controls = list_module_b_controls()
    assert len(controls) == 7
    assert controls[0]["ref"] == "B.1.1"


def test_get_control_returns_b31_details() -> None:
    control = get_control("B.3.1")
    assert control["found"] is True
    assert (
        "Azure AI Foundry" in control["requirement"] or "Azure AI Foundry" in control["azure_focus"]
    )


def test_validate_evidence_filename_accepts_dotted_control_ref() -> None:
    result = validate_evidence_filename("B.2.1_SolutionDesign_v1.pdf")
    assert result["valid"] is True
    assert result["control_ref"] == "B.2.1"
    assert result["version"] == 1


def test_validate_evidence_filename_rejects_unknown_control() -> None:
    result = validate_evidence_filename("B.9.9_SolutionDesign_v1.pdf")
    assert result["valid"] is False
    assert "not a known" in result["message"]


def test_score_waf_pillar_returns_weighted_rating() -> None:
    result = score_waf_pillar(
        "security",
        {"identity": True, "network": 0.5, "data": 100, "safety": "partial", "logging": False},
    )
    assert result["valid"] is True
    assert result["score"] == 65
    assert result["rating"] == "adequate"


def test_create_server_registers_fastmcp_server() -> None:
    server = create_server()
    assert server.name == "contoso-module-b-lab"
