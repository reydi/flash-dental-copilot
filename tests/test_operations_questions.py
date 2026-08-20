"""Tests for the operational dashboard answers: reliability, blocked, compliance, backlog."""
from __future__ import annotations

from flash_dental_copilot.kpi_computation import ServiceTicket
from flash_dental_copilot.operations_questions import answer_operations_question
from flash_dental_copilot.structured_analytics import MaintenanceRecord


def _ticket(serial, model, status="finished", category="service", hold_reason="", technician="Yudi"):
    return ServiceTicket("T", serial, technician, True, 5, status, category, "Klinik", "City", model, hold_reason)


def test_reliability_names_the_worst_model():
    tickets = [_ticket("A", "DC-300"), _ticket("A", "DC-300"), _ticket("B", "DC-500")]
    answer = answer_operations_question("which product is least reliable?", tickets, [])
    assert answer is not None
    assert "DC-300" in answer.answer_text and answer.visualization["kind"] == "bar"


def test_waiting_on_spare_part_is_counted():
    tickets = [
        _ticket("A", "DC-300", "outstanding", hold_reason="spare part"),
        _ticket("B", "DC-300", "outstanding", hold_reason="customer approval"),
    ]
    answer = answer_operations_question("how many tickets are waiting on a spare part?", tickets, [])
    assert answer is not None and "1 open" in answer.answer_text


def test_maintenance_compliance_rate_is_computed_as_a_stat():
    schedule = [
        MaintenanceRecord("A", "2025-01-15", True),
        MaintenanceRecord("B", "2026-05-15", False),
        MaintenanceRecord("C", "2026-06-15", False),
    ]
    answer = answer_operations_question("what's the on-time maintenance compliance?", [], schedule)
    assert answer is not None and answer.visualization["kind"] == "stat" and "66.7%" in answer.answer_text


def test_backlog_names_the_technician_with_the_most_open_tickets():
    tickets = [
        _ticket("A", "DC-300", "outstanding", technician="Dedi"),
        _ticket("B", "DC-300", "outstanding", technician="Dedi"),
        _ticket("C", "DC-300", "outstanding", technician="Yudi"),
    ]
    answer = answer_operations_question("which technician has the biggest backlog?", tickets, [])
    assert answer is not None and "Dedi" in answer.answer_text


def test_unrelated_question_defers():
    assert answer_operations_question("who is the best football player?", [], []) is None
