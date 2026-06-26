"""Embedded Module B control and WAF scoring data."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ModuleBControl:
    """A Module B specialization control used by the lab MCP server."""

    ref: str
    title: str
    requirement: str
    evidence: tuple[str, ...]
    azure_focus: str


MODULE_B_CONTROLS: tuple[ModuleBControl, ...] = (
    ModuleBControl(
        ref="B.1.1",
        title="Portfolio Assessment",
        requirement="Assess three customer AI opportunities, including AI-powered app fit.",
        evidence=("assessment summary", "use-case prioritisation", "customer sign-off"),
        azure_focus="Azure AI Foundry project fit, data readiness, and GitHub Models lab path.",
    ),
    ModuleBControl(
        ref="B.2.1",
        title="Solution Design and Responsible AI",
        requirement="Produce solution design evidence with RAI Standard V2 and impact assessment.",
        evidence=("high-level design", "Customer Impact Assessment", "RAI risk register"),
        azure_focus="Azure AI Foundry, content safety, groundedness, and identity boundaries.",
    ),
    ModuleBControl(
        ref="B.2.2",
        title="Well-Architected Review",
        requirement="Run two applicable WAF pillars for three AI workloads.",
        evidence=("WAF assessment export", "pillar remediation plan", "owner tracker"),
        azure_focus=(
            "Reliability, Security, Performance Efficiency, Cost, and Operational Excellence."
        ),
    ),
    ModuleBControl(
        ref="B.2.3",
        title="Proof of Concept or Pilot",
        requirement="Demonstrate a PoC or pilot that includes Azure AI Foundry results.",
        evidence=("pilot report", "evaluation results", "go/no-go decision"),
        azure_focus="Foundry evaluation, prompt flow, model comparison, and deployment readiness.",
    ),
    ModuleBControl(
        ref="B.3.1",
        title="Deployment",
        requirement="Deploy three customer AI workloads with an Azure AI Foundry component.",
        evidence=("deployment architecture", "release evidence", "Foundry project screenshot"),
        azure_focus=(
            "Azure AI Foundry Agent Service, Azure OpenAI, managed identity, and monitoring."
        ),
    ),
    ModuleBControl(
        ref="B.4.1",
        title="Service Validation and Testing",
        requirement=(
            "Validate deployed services and complete post-deployment Operational Excellence review."
        ),
        evidence=("test plan", "test results", "post-deployment WAF export"),
        azure_focus="Evaluation gates, load testing, telemetry, and incident runbooks.",
    ),
    ModuleBControl(
        ref="B.4.2",
        title="Post-Deployment Documentation",
        requirement="Hand over design and BAU operations documentation for deployed workloads.",
        evidence=("runbook", "knowledge transfer plan", "hypercare plan"),
        azure_focus=(
            "Azure Monitor, Foundry operations, rollback, quota, and content safety runbooks."
        ),
    ),
)

WAF_PILLAR_WEIGHTS: dict[str, dict[str, float]] = {
    "reliability": {"slo": 0.25, "redundancy": 0.2, "dr": 0.2, "quota": 0.2, "testing": 0.15},
    "security": {"identity": 0.25, "network": 0.2, "data": 0.2, "safety": 0.2, "logging": 0.15},
    "performance": {"sizing": 0.25, "autoscale": 0.2, "latency": 0.2, "cache": 0.15, "load": 0.2},
    "cost": {
        "budget": 0.25,
        "rightsize": 0.25,
        "tokens": 0.2,
        "shutdown": 0.15,
        "chargeback": 0.15,
    },
    "operations": {"runbook": 0.25, "alerts": 0.2, "deployment": 0.2, "evals": 0.2, "kt": 0.15},
}
