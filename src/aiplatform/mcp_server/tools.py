"""Pure Python tool functions exposed by the Module B MCP server."""

from __future__ import annotations

import re
from typing import Any

from aiplatform.mcp_server.data import MODULE_B_CONTROLS, WAF_PILLAR_WEIGHTS, ModuleBControl

_CONTROL_LOOKUP = {control.ref.upper(): control for control in MODULE_B_CONTROLS}
_FILENAME_PATTERN = re.compile(
    r"^(?P<control>B(?:\.\d+){2}|B\d+\.\d+)_(?P<document>[A-Za-z][A-Za-z0-9-]*)_v(?P<version>[1-9]\d*)"
    r"(?P<extension>\.(?:pdf|docx|xlsx|md))?$",
    re.IGNORECASE,
)
STRONG_SCORE = 85
ADEQUATE_SCORE = 65
REMEDIATION_SCORE = 40


def list_module_b_controls() -> list[dict[str, Any]]:
    """List all embedded Module B controls."""
    return [_control_to_dict(control, include_details=False) for control in MODULE_B_CONTROLS]


def get_control(ref: str) -> dict[str, Any]:
    """Return detailed requirements for a Module B control.

    Args:
        ref: Control reference such as ``B.3.1``.

    Returns:
        Control details or an error payload when the control is unknown.
    """
    normalised = _normalise_control_ref(ref)
    control = _CONTROL_LOOKUP.get(normalised)
    if control is None:
        return {
            "found": False,
            "ref": ref,
            "error": "Unknown Module B control",
            "known_refs": [item.ref for item in MODULE_B_CONTROLS],
        }
    payload = _control_to_dict(control, include_details=True)
    payload["found"] = True
    return payload


def validate_evidence_filename(name: str) -> dict[str, Any]:
    """Validate the ``[ControlRef]_[DocumentType]_v[N]`` evidence convention.

    Args:
        name: Candidate file name, optionally including an allowed extension.

    Returns:
        Validation result with parsed fields and remediation guidance.
    """
    match = _FILENAME_PATTERN.fullmatch(name.strip())
    if match is None:
        return {
            "valid": False,
            "name": name,
            "message": (
                "Use [ControlRef]_[DocumentType]_v[N].pdf, for example B.3.1_SolutionDesign_v1.pdf."
            ),
        }
    control_ref = _normalise_control_ref(match.group("control"))
    known = control_ref in _CONTROL_LOOKUP
    return {
        "valid": known,
        "name": name,
        "control_ref": control_ref,
        "document_type": match.group("document"),
        "version": int(match.group("version")),
        "extension": match.group("extension") or "",
        "message": "Filename is valid."
        if known
        else "Control reference is not a known Module B control.",
    }


def score_waf_pillar(pillar: str, answers: dict[str, Any]) -> dict[str, Any]:
    """Score a Well-Architected AI workload pillar with simple weights.

    Args:
        pillar: Pillar name such as ``security`` or ``reliability``.
        answers: Mapping of scoring criteria to booleans or numeric values from 0 to 1/100.

    Returns:
        Weighted score with missing criteria and recommendation.
    """
    key = _normalise_pillar(pillar)
    weights = WAF_PILLAR_WEIGHTS.get(key)
    if weights is None:
        return {
            "valid": False,
            "pillar": pillar,
            "error": "Unknown WAF pillar",
            "known_pillars": sorted(WAF_PILLAR_WEIGHTS),
        }
    weighted = 0.0
    missing: list[str] = []
    for criterion, weight in weights.items():
        if criterion not in answers:
            missing.append(criterion)
            continue
        weighted += _answer_value(answers[criterion]) * weight
    score = round(weighted * 100)
    return {
        "valid": True,
        "pillar": key,
        "score": score,
        "rating": _rating(score),
        "missing_criteria": missing,
        "recommendation": _recommendation(score, missing),
    }


def _control_to_dict(control: ModuleBControl, *, include_details: bool) -> dict[str, Any]:
    """Convert a control dataclass to a serialisable dictionary."""
    payload: dict[str, Any] = {"ref": control.ref, "title": control.title}
    if include_details:
        payload.update(
            {
                "requirement": control.requirement,
                "evidence": list(control.evidence),
                "azure_focus": control.azure_focus,
            }
        )
    return payload


def _normalise_control_ref(ref: str) -> str:
    """Normalise compact and dotted Module B refs to dotted form."""
    clean = ref.strip().upper()
    if re.fullmatch(r"B\d+\.\d+", clean):
        return f"B.{clean[1:]}"
    return clean


def _normalise_pillar(pillar: str) -> str:
    """Normalise common WAF pillar aliases."""
    clean = pillar.strip().lower().replace("-", " ").replace("_", " ")
    aliases = {
        "operational excellence": "operations",
        "operation": "operations",
        "ops": "operations",
        "performance efficiency": "performance",
        "cost optimization": "cost",
        "cost optimisation": "cost",
    }
    return aliases.get(clean, clean)


def _answer_value(value: Any) -> float:
    """Convert an answer value to a normalised score from 0 to 1."""
    if isinstance(value, bool):
        return 1.0 if value else 0.0
    if isinstance(value, int | float):
        numeric = float(value)
        if numeric > 1:
            numeric /= 100
        return min(max(numeric, 0.0), 1.0)
    if isinstance(value, str):
        clean = value.strip().lower()
        if clean in {"yes", "true", "done", "complete", "implemented"}:
            return 1.0
        if clean in {"partial", "partly", "in progress"}:
            return 0.5
    return 0.0


def _rating(score: int) -> str:
    """Return a textual maturity rating."""
    if score >= STRONG_SCORE:
        return "strong"
    if score >= ADEQUATE_SCORE:
        return "adequate"
    if score >= REMEDIATION_SCORE:
        return "needs_remediation"
    return "high_risk"


def _recommendation(score: int, missing: list[str]) -> str:
    """Return a short remediation recommendation."""
    if missing:
        return "Complete missing criteria: " + ", ".join(missing)
    if score < ADEQUATE_SCORE:
        return "Prioritise remediation before audit evidence sign-off."
    return "Ready to include in the Module B evidence pack."
