"""Guardrail result models."""

from __future__ import annotations

from pydantic import BaseModel, Field


class GuardrailResult(BaseModel):
    """Result returned by guardrail checks."""

    allowed: bool
    reasons: list[str] = Field(default_factory=list)
    redacted_text: str | None = None
