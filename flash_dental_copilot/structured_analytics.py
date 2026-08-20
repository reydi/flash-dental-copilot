"""Compute answers to analytical questions from structured service data.

Single responsibility: the aggregate numbers a cockpit answers — job counts by
category, technician rankings, overdue-maintenance counts. Computed by code, so
the copilot can state a number it did not invent.
"""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

from flash_dental_copilot.kpi_computation import (
    ServiceTicket,
    compute_technician_first_time_fix_rate_percent,
)


@dataclass(frozen=True)
class MaintenanceRecord:
    """One unit's next scheduled maintenance, and whether it is already overdue."""
    unit_serial: str
    next_maintenance_due: str
    is_overdue: bool


def count_jobs_by_category(service_tickets: list[ServiceTicket]) -> dict[str, int]:
    """How many tickets fall in each job category (service, maintenance, …)."""
    return dict(Counter(ticket.job_category for ticket in service_tickets))


def count_jobs_in_categories(
    service_tickets: list[ServiceTicket], categories: set[str]
) -> int:
    """How many tickets fall in the given set of job categories, combined."""
    return sum(1 for ticket in service_tickets if ticket.job_category in categories)


def rank_technicians_by_first_time_fix(
    service_tickets: list[ServiceTicket],
) -> list[tuple[str, float]]:
    """Every technician with a computed first-time-fix rate, best first."""
    technician_names = sorted({ticket.technician_name for ticket in service_tickets})
    ranked = [
        (name, compute_technician_first_time_fix_rate_percent(service_tickets, name))
        for name in technician_names
    ]
    ranked_with_rate = [(name, rate) for name, rate in ranked if rate is not None]
    ranked_with_rate.sort(key=lambda pair: pair[1], reverse=True)
    return ranked_with_rate


def count_overdue_maintenance(
    maintenance_schedule: list[MaintenanceRecord],
) -> int:
    """How many units are past their scheduled preventive-maintenance date."""
    return sum(1 for record in maintenance_schedule if record.is_overdue)


def list_clinics_for_technician(
    service_tickets: list[ServiceTicket], technician_name: str
) -> list[tuple[str, str]]:
    """The distinct (clinic, city) pairs a technician has serviced, alphabetical."""
    clinics = {
        (ticket.clinic_name, ticket.city)
        for ticket in service_tickets
        if ticket.technician_name == technician_name and ticket.clinic_name
    }
    return sorted(clinics)
