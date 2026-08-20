"""Tests for the computed aggregates: category counts, rankings, overdue maintenance."""
from __future__ import annotations

from flash_dental_copilot.kpi_computation import ServiceTicket
from flash_dental_copilot.structured_analytics import (
    MaintenanceRecord,
    count_jobs_in_categories,
    count_overdue_maintenance,
    rank_technicians_by_first_time_fix,
)


def _ticket(technician_name: str, was_fixed: bool, category: str, status: str = "finished") -> ServiceTicket:
    return ServiceTicket("TKT-0001", "EX9", technician_name, was_fixed, 5, status, category)


def test_count_jobs_in_categories_sums_the_named_categories():
    tickets = [
        _ticket("Yudi Pratama", True, "service"),
        _ticket("Yudi Pratama", True, "maintenance"),
        _ticket("Dedi Kurniawan", True, "survey"),
    ]
    assert count_jobs_in_categories(tickets, {"service", "maintenance"}) == 2


def test_rank_technicians_orders_best_first_worst_last():
    tickets = [
        _ticket("Yudi Pratama", True, "service"),
        _ticket("Yudi Pratama", True, "service"),
        _ticket("Dedi Kurniawan", False, "service"),
        _ticket("Dedi Kurniawan", True, "service"),
    ]
    ranked = rank_technicians_by_first_time_fix(tickets)
    assert ranked[0][0] == "Yudi Pratama"  # 100%
    assert ranked[-1][0] == "Dedi Kurniawan"  # 50%


def test_count_overdue_maintenance_counts_only_overdue_records():
    schedule = [
        MaintenanceRecord("EX9a", "2025-01-15", True),
        MaintenanceRecord("EX9b", "2026-05-15", False),
        MaintenanceRecord("EX9c", "2025-03-15", True),
    ]
    assert count_overdue_maintenance(schedule) == 2
