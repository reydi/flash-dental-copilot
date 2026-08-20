"""Tests for the analytical/lookup router: aggregate questions are computed, lookups defer."""
from __future__ import annotations

from flash_dental_copilot.employee_records import Employee
from flash_dental_copilot.kpi_computation import ServiceTicket
from flash_dental_copilot.question_router import answer_analytical_question
from flash_dental_copilot.structured_analytics import MaintenanceRecord

TICKETS = [
    ServiceTicket("T1", "EX9", "Yudi Pratama", True, 5, "finished", "service"),
    ServiceTicket("T2", "EX9", "Yudi Pratama", True, 5, "finished", "maintenance"),
    ServiceTicket("T3", "EX9", "Arman Hakim", False, 5, "finished", "service"),
    ServiceTicket("T4", "EX9", "Yudi Pratama", False, 5, "outstanding", "service"),
]
SCHEDULE = [
    MaintenanceRecord("EX9a", "2025-01-15", True),
    MaintenanceRecord("EX9b", "2026-05-15", False),
]
EMPLOYEES = [
    Employee("EMP-1", "A", "Field Technician", "Jabodetabek"),
    Employee("EMP-2", "B", "Field Technician", "Sumatra"),
    Employee("EMP-3", "C", "Sales Representative", "West Java"),
]


def test_headcount_by_role_is_computed_from_the_directory():
    answer = answer_analytical_question(
        "how many field technicians do we have?", TICKETS, SCHEDULE, EMPLOYEES
    )
    assert answer is not None and "2 Field Technician" in answer.answer_text


def test_total_headcount_is_computed():
    answer = answer_analytical_question(
        "how many people work at Flash Dental?", TICKETS, SCHEDULE, EMPLOYEES
    )
    assert answer is not None and "3 employees" in answer.answer_text


def test_headcount_question_defers_when_no_directory_is_supplied():
    assert answer_analytical_question("how many field technicians?", TICKETS, SCHEDULE) is None


def test_delayed_maintenance_question_is_computed():
    answer = answer_analytical_question("how many delayed maintenance do we have?", TICKETS, SCHEDULE)
    assert answer is not None and "1" in answer.answer_text


def test_least_performing_technician_is_computed():
    answer = answer_analytical_question("who is the least performing technician this month?", TICKETS, SCHEDULE)
    assert answer is not None and "Arman Hakim" in answer.answer_text


def test_how_many_jobs_by_category_is_computed():
    answer = answer_analytical_question("how many maintenance and service jobs last month?", TICKETS, SCHEDULE)
    assert answer is not None and "4" in answer.answer_text


def test_factual_lookup_defers_to_retrieval():
    assert answer_analytical_question("show FD-1042 service history", TICKETS, SCHEDULE) is None
