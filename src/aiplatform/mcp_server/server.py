"""STDIO MCP server exposing Module B helper tools."""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from aiplatform.mcp_server.tools import (
    get_control,
    list_module_b_controls,
    score_waf_pillar,
    validate_evidence_filename,
)


def create_server() -> FastMCP:
    """Create and register the custom lab MCP server."""
    mcp = FastMCP(
        "contoso-module-b-lab",
        instructions=(
            "Module B helper tools for the Contoso AI Assistant Train-the-Trainer MicroHack."
        ),
    )

    @mcp.tool(name="list_module_b_controls")
    def list_module_b_controls_tool() -> list[dict[str, Any]]:
        """List Module B controls with references and titles."""
        return list_module_b_controls()

    @mcp.tool(name="get_control")
    def get_control_tool(ref: str) -> dict[str, Any]:
        """Return detailed requirements for a Module B control reference."""
        return get_control(ref)

    @mcp.tool(name="validate_evidence_filename")
    def validate_evidence_filename_tool(name: str) -> dict[str, Any]:
        """Validate a Module B evidence filename."""
        return validate_evidence_filename(name)

    @mcp.tool(name="score_waf_pillar")
    def score_waf_pillar_tool(pillar: str, answers: dict[str, Any]) -> dict[str, Any]:
        """Score a WAF pillar for an AI workload."""
        return score_waf_pillar(pillar, answers)

    return mcp


def main() -> None:
    """Run the MCP server over STDIO."""
    create_server().run(transport="stdio")


if __name__ == "__main__":
    main()
