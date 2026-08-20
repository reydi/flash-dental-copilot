"""Tests for PII de-identification: names, serials, and phone numbers become tokens."""
from __future__ import annotations

from flash_dental_copilot.pii_redaction import redact_personally_identifiable_information


def test_person_serial_and_phone_are_all_replaced_with_tokens():
    result = redact_personally_identifiable_information(
        "Report: Yudi Pratama serviced serial FD-1042; contact 0812-3456-7890."
    )
    assert "Yudi Pratama" not in result.redacted_text
    assert "FD-1042" not in result.redacted_text
    assert "0812-3456-7890" not in result.redacted_text
    assert "[PERSON_1]" in result.redacted_text
    assert "[SERIAL_1]" in result.redacted_text
    assert "[PHONE_1]" in result.redacted_text


def test_vault_maps_every_token_back_to_its_original_value():
    result = redact_personally_identifiable_information(
        "Yudi Pratama serviced FD-1042."
    )
    assert result.token_to_original_value["[PERSON_1]"] == "Yudi Pratama"
    assert result.token_to_original_value["[SERIAL_1]"] == "FD-1042"


def test_text_without_pii_is_left_unchanged():
    result = redact_personally_identifiable_information("replaced the suction motor")
    assert result.redacted_text == "replaced the suction motor"
    assert result.token_to_original_value == {}
