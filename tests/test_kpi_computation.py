"""Tests for the deterministic KPI computations."""
from __future__ import annotations

from flash_dental_copilot.kpi_computation import (
    ServiceTicket,
    compute_average_cycle_time_days,
    compute_first_time_fix_rate_percent,
    compute_technician_first_time_fix_rate_percent,
    compute_warranty_expiry_date,
    count_outstanding_jobs,
)


def _ticket(
    technician_name: str,
    was_fixed_first_visit: bool,
    cycle_time_days: int,
    status: str,
) -> ServiceTicket:
    return ServiceTicket(
        ticket_id="TKT-0001",
        unit_serial="EX92026030001",
        technician_name=technician_name,
        was_fixed_first_visit=was_fixed_first_visit,
        cycle_time_days=cycle_time_days,
        status=status,
    )


def test_first_time_fix_rate_counts_only_finished_jobs():
    tickets = [
        _ticket("Yudi Pratama", True, 5, "finished"),
        _ticket("Yudi Pratama", False, 9, "finished"),
        _ticket("Yudi Pratama", False, 3, "outstanding"),  # open, ignored
    ]
    assert compute_first_time_fix_rate_percent(tickets) == 50.0


def test_average_cycle_time_is_mean_of_finished_jobs():
    tickets = [
        _ticket("Dedi Kurniawan", True, 4, "finished"),
        _ticket("Dedi Kurniawan", True, 10, "finished"),
    ]
    assert compute_average_cycle_time_days(tickets) == 7.0


def test_technician_rate_isolates_one_technician():
    tickets = [
        _ticket("Yudi Pratama", True, 5, "finished"),
        _ticket("Dedi Kurniawan", False, 5, "finished"),
    ]
    assert compute_technician_first_time_fix_rate_percent(tickets, "Yudi Pratama") == 100.0


def test_outstanding_jobs_exclude_finished_and_cancelled():
    tickets = [
        _ticket("Yudi Pratama", True, 5, "finished"),
        _ticket("Yudi Pratama", False, 5, "outstanding"),
        _ticket("Yudi Pratama", False, 5, "cancelled"),
    ]
    assert count_outstanding_jobs(tickets) == 1


def test_kpis_return_none_when_there_are_no_finished_jobs():
    assert compute_first_time_fix_rate_percent([]) is None
    assert compute_average_cycle_time_days([]) is None


def test_warranty_expiry_adds_whole_years_to_the_purchase_date():
    assert compute_warranty_expiry_date("2023-06-15", 2) == "2025-06-15"
