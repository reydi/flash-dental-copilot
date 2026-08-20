"""Tests for the region SLA-capacity answer: an understaffed region is flagged on a map."""
from __future__ import annotations

from flash_dental_copilot.capacity_planning import answer_capacity_question
from flash_dental_copilot.employee_records import Employee
from flash_dental_copilot.kpi_computation import ServiceTicket


def _technician(region: str) -> Employee:
    return Employee("EMP-1", "Someone", "Field Technician", region)


def _ticket_in(city: str) -> ServiceTicket:
    return ServiceTicket("T", "EX9", "Yudi", True, 5, "finished", "service", "Klinik", city)


def test_capacity_question_flags_an_understaffed_region_as_a_map():
    employees = [_technician("Kalimantan")]  # one technician for the whole region
    tickets = [_ticket_in("Samarinda") for _ in range(60)]  # 60 Kalimantan jobs
    answer = answer_capacity_question(
        "do we have enough technicians for the 3-day sla in all cities?", employees, tickets
    )
    assert answer is not None
    assert answer.visualization["kind"] == "map"
    assert "can't hold" in answer.answer_text
    kalimantan = next(r for r in answer.visualization["regions"] if r["region"] == "Kalimantan")
    assert kalimantan["severity"] == "critical"


def test_non_capacity_question_defers():
    assert answer_capacity_question(
        "who is the best technician?", [_technician("Sumatra")], [_ticket_in("Medan")]
    ) is None
