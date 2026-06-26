"""PII and secret detection for generated answers."""

from __future__ import annotations

import re

EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
PHONE_RE = re.compile(r"(?<!\d)(?:\+?\d[\d .()/-]{7,}\d)(?!\d)")
CARD_RE = re.compile(r"(?<!\d)(?:\d[ -]?){13,19}(?!\d)")
SECRET_RE = re.compile(
    r"\b(?:api[_-]?key|token|secret|credential)\b\s*[:=]\s*['\"]?([A-Za-z0-9_\-]{12,})",
    re.IGNORECASE,
)
MIN_CARD_DIGITS = 13
MAX_CARD_DIGITS = 19
LUHN_MAX_SINGLE_DIGIT = 9


def redact_sensitive_text(text: str) -> tuple[str, list[str]]:
    """Redact PII and secret-like values.

    Args:
        text: Text to inspect.

    Returns:
        Redacted text and reasons for any replacements.
    """
    redacted = text
    reasons: list[str] = []
    redacted, email_count = EMAIL_RE.subn("[REDACTED_EMAIL]", redacted)
    if email_count:
        reasons.append("Detected and redacted email address.")
    redacted, phone_count = PHONE_RE.subn(_redact_phone_or_card, redacted)
    if phone_count:
        reasons.append("Detected and redacted phone-like number.")
    redacted, card_count = CARD_RE.subn(_redact_card_if_valid, redacted)
    if card_count:
        reasons.append("Detected and redacted credit-card-like number.")
    redacted, secret_count = SECRET_RE.subn(_redact_secret, redacted)
    if secret_count:
        reasons.append("Detected and redacted secret-like value.")
    return redacted, reasons


def _redact_phone_or_card(match: re.Match[str]) -> str:
    value = match.group(0)
    digits = _digits(value)
    if MIN_CARD_DIGITS <= len(digits) <= MAX_CARD_DIGITS and _passes_luhn(digits):
        return "[REDACTED_CARD]"
    return "[REDACTED_PHONE]"


def _redact_card_if_valid(match: re.Match[str]) -> str:
    value = match.group(0)
    digits = _digits(value)
    if _passes_luhn(digits):
        return "[REDACTED_CARD]"
    return value


def _redact_secret(match: re.Match[str]) -> str:
    prefix = match.group(0)[: match.start(1) - match.start(0)]
    return f"{prefix}[REDACTED_SECRET]"


def _digits(value: str) -> str:
    return "".join(character for character in value if character.isdigit())


def _passes_luhn(digits: str) -> bool:
    if not digits.isdigit() or len(digits) < MIN_CARD_DIGITS:
        return False
    total = 0
    parity = len(digits) % 2
    for index, character in enumerate(digits):
        digit = int(character)
        if index % 2 == parity:
            digit *= 2
            if digit > LUHN_MAX_SINGLE_DIGIT:
                digit -= LUHN_MAX_SINGLE_DIGIT
        total += digit
    return total % 10 == 0
