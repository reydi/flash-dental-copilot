"""De-identify personally identifiable information before it leaves the boundary.

Single responsibility: replace names, unit serials, and phone numbers with stable
tokens, and return the reversible mapping (the "vault"). In production this is
Cloud DLP; the contract — the model only ever sees stand-ins — is identical.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

# Two capitalised words in a row read as a person's name (e.g. "Yudi Pratama").
_PERSON_NAME_PATTERN = re.compile(r"\b[A-Z][a-z]+ [A-Z][a-z]+\b")
# Flash Dental unit serials: FD-1042 style, and the EX9/Tealth stock formats.
_UNIT_SERIAL_PATTERN = re.compile(r"\b(?:FD-\d+|EX9\d{7,}|TEALTH[- ]?\w+)\b")
# Indonesian mobile numbers, e.g. 0812-3456-7890.
_PHONE_NUMBER_PATTERN = re.compile(r"\b0\d{2,3}-\d{3,4}-\d{3,4}\b")


@dataclass(frozen=True)
class RedactionResult:
    """The de-identified text plus the token -> original-value vault."""
    redacted_text: str
    token_to_original_value: dict[str, str]


def redact_personally_identifiable_information(text: str) -> RedactionResult:
    """Replace people, serials, and phone numbers with [KIND_N] tokens."""
    token_to_original_value: dict[str, str] = {}
    running_counts: dict[str, int] = {"PERSON": 0, "SERIAL": 0, "PHONE": 0}

    def replace_with_token(kind: str, matched_value: str) -> str:
        running_counts[kind] += 1
        token = f"[{kind}_{running_counts[kind]}]"
        token_to_original_value[token] = matched_value
        return token

    redacted_text = _PERSON_NAME_PATTERN.sub(
        lambda match: replace_with_token("PERSON", match.group(0)), text
    )
    redacted_text = _UNIT_SERIAL_PATTERN.sub(
        lambda match: replace_with_token("SERIAL", match.group(0)), redacted_text
    )
    redacted_text = _PHONE_NUMBER_PATTERN.sub(
        lambda match: replace_with_token("PHONE", match.group(0)), redacted_text
    )
    return RedactionResult(
        redacted_text=redacted_text,
        token_to_original_value=token_to_original_value,
    )
