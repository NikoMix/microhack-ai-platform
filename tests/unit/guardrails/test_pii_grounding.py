from __future__ import annotations

import re
from importlib import import_module
from typing import Any


def _aiplatform_module(*parts: str) -> Any:
    return import_module(".".join(("aiplatform", *parts)))


pii = _aiplatform_module("guardrails", "pii")
grounding = _aiplatform_module("guardrails", "grounding")
check_groundedness = grounding.check_groundedness
RetrievedChunk = _aiplatform_module("rag", "types").RetrievedChunk


def test_pii_redacts_phone_card_secret_and_preserves_invalid_card() -> None:
    text = (
        "Call +1 (425) 555-0100. "
        "Use token='abcdefghijklmnopqrstuvwxyz'. "
        "Card candidate 1234 5678 9012 3456."
    )

    redacted, reasons = pii.redact_sensitive_text(text)

    assert "[REDACTED_PHONE]" in redacted
    assert "token='[REDACTED_SECRET]'" in redacted
    assert "1234 5678 9012 3456" not in redacted
    assert "Detected and redacted phone-like number." in reasons
    assert "Detected and redacted secret-like value." in reasons

    match = pii.CARD_RE.search("1234 5678 9012 3456")
    assert match is not None
    assert pii._redact_card_if_valid(match) == "1234 5678 9012 3456"


def test_pii_private_helpers_cover_luhn_and_secret_prefixes() -> None:
    assert pii._digits("ab12 cd34") == "1234"
    assert not pii._passes_luhn("not-digits")
    assert not pii._passes_luhn("123")
    assert pii._passes_luhn("4111111111111111")

    match = pii.SECRET_RE.search("api_key: abcdefghijklmnop")
    assert match is not None
    assert pii._redact_secret(match) == "api_key: [REDACTED_SECRET]"

    manual_match = re.search(r"(?:\d[ -]?){13,19}", "4111 1111 1111 1111")
    assert manual_match is not None
    assert pii._redact_card_if_valid(manual_match) == "[REDACTED_CARD]"


def test_grounding_allows_uncertainty_and_empty_answers() -> None:
    context = [RetrievedChunk(text="", source="empty.md", score=1.0)]

    assert check_groundedness("I do not know; contact the service desk.", []) == []
    assert check_groundedness("and the you", context) == []
    assert check_groundedness("Specific unsupported answer", context) == [
        "No retrieved context was available to ground the answer."
    ]


def test_grounding_flags_low_overlap() -> None:
    context = [
        RetrievedChunk(
            text="Payroll questions use the HR portal.",
            source="hr.md",
            score=0.8,
        )
    ]

    assert check_groundedness("Quantum network access requires blue bananas.", context) == [
        "Answer appears insufficiently supported by retrieved context."
    ]
