"""Responsible AI guardrails for Contoso AI Assistant."""

from __future__ import annotations

from aiplatform.guardrails.facade import Guardrails
from aiplatform.guardrails.models import GuardrailResult

__all__ = ["GuardrailResult", "Guardrails"]
