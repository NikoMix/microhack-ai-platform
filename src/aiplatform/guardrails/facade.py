"""Facade for Responsible AI guardrails."""

from __future__ import annotations

from collections.abc import Sequence

from aiplatform.config import Settings, get_settings
from aiplatform.guardrails.grounding import check_groundedness
from aiplatform.guardrails.input_shield import detect_prompt_attack
from aiplatform.guardrails.models import GuardrailResult
from aiplatform.guardrails.pii import redact_sensitive_text
from aiplatform.rag import RetrievedChunk


class Guardrails:
    """Responsible AI guardrail facade used by apps, agents, and tests."""

    def __init__(self, settings: Settings | None = None) -> None:
        """Create guardrails with optional settings override."""
        self._settings = settings or get_settings()

    async def check_input(self, text: str) -> GuardrailResult:
        """Check user input for prompt-injection and jailbreak attempts."""
        reasons = await detect_prompt_attack(text, self._settings)
        return GuardrailResult(allowed=not reasons, reasons=reasons, redacted_text=text)

    async def check_output(
        self,
        answer: str,
        context: Sequence[RetrievedChunk],
    ) -> GuardrailResult:
        """Check and redact assistant output before returning it."""
        redacted, reasons = redact_sensitive_text(answer)
        reasons.extend(check_groundedness(redacted, context))
        return GuardrailResult(allowed=not reasons, reasons=reasons, redacted_text=redacted)
