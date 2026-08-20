"""Load structured service tickets and summarise them into per-domain KPI lines.

Single responsibility: bridge the on-disk ticket records to the pure KPI
functions, so /ask can return a computed, defensible number with each answer.
"""
from __future__ import annotations

import json

from flash_dental_copilot.corpus import DATA_DIRECTORY
from flash_dental_copilot.kpi_computation import (
    ServiceTicket,
    compute_average_cycle_time_days,
    compute_first_time_fix_rate_percent,
    compute_technician_first_time_fix_rate_percent,
    compute_warranty_expiry_date,
    count_outstanding_jobs,
)
from flash_dental_copilot.structured_analytics import MaintenanceRecord

SERVICE_TICKETS_FILENAME = "service_tickets.json"
MAINTENANCE_SCHEDULE_FILENAME = "maintenance_schedule.json"

# The unit and technician the demo tells its story around.
FEATURED_UNIT_SERIAL = "FD-1042"
FEATURED_UNIT_PURCHASE_DATE = "2023-06-15"
FEATURED_TECHNICIAN_NAME = "Yudi Pratama"
MACHINE_WARRANTY_YEARS = 2


def load_service_tickets() -> list[ServiceTicket]:
    """Read the structured tickets the KPI numbers are computed from."""
    tickets_file = DATA_DIRECTORY / SERVICE_TICKETS_FILENAME
    raw_tickets = json.loads(tickets_file.read_text(encoding="utf-8"))
    return [ServiceTicket(**ticket_fields) for ticket_fields in raw_tickets]


def load_maintenance_schedule() -> list[MaintenanceRecord]:
    """Read each unit's next preventive-maintenance date and overdue flag."""
    schedule_file = DATA_DIRECTORY / MAINTENANCE_SCHEDULE_FILENAME
    raw_records = json.loads(schedule_file.read_text(encoding="utf-8"))
    return [MaintenanceRecord(**record_fields) for record_fields in raw_records]


def build_domain_kpi_summary(
    domain_name: str, service_tickets: list[ServiceTicket]
) -> str:
    """One line of computed KPIs to accompany an answer in the given domain."""
    if domain_name == "assets":
        first_time_fix_rate = compute_first_time_fix_rate_percent(service_tickets)
        warranty_expiry_date = compute_warranty_expiry_date(
            FEATURED_UNIT_PURCHASE_DATE, MACHINE_WARRANTY_YEARS
        )
        outstanding_job_count = count_outstanding_jobs(service_tickets)
        return (
            f"first-time-fix {first_time_fix_rate}% · "
            f"{FEATURED_UNIT_SERIAL} warranty → {warranty_expiry_date} · "
            f"{outstanding_job_count} outstanding jobs"
        )
    technician_first_time_fix_rate = compute_technician_first_time_fix_rate_percent(
        service_tickets, FEATURED_TECHNICIAN_NAME
    )
    average_cycle_time_days = compute_average_cycle_time_days(service_tickets)
    technician_given_name = FEATURED_TECHNICIAN_NAME.split()[0]
    return (
        f"{technician_given_name} first-time-fix {technician_first_time_fix_rate}% · "
        f"avg cycle time {average_cycle_time_days} days (computed)"
    )
