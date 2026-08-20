"""Answer 'do we have enough technicians for the SLA in every region?' by computing it.

Single responsibility: fold technician headcount and ticket demand up to the nine
service regions, classify each region's SLA risk, and phrase the computed answer with
a severity map. This is the capacity question the C-level cockpit exists to answer.
"""
from __future__ import annotations

from collections import Counter
from typing import Optional

from flash_dental_copilot import visualizations
from flash_dental_copilot.analytics_common import ComputedAnswer, mentions_any
from flash_dental_copilot.employee_records import Employee
from flash_dental_copilot.geography import SERVICE_REGIONS, region_for_city
from flash_dental_copilot.kpi_computation import ServiceTicket

_FIELD_TECHNICIAN_ROLE = "Field Technician"
# The question must be about capacity/SLA AND about technicians/regions to route here.
_CAPACITY_SIGNAL = (
    "enough", "capacity", "coverage", "cover ", "understaff", "staffing",
    "3-day", "3 working", "3-working", "working day", "working-day", "within", "handle all", "in all",
)
_SCOPE_SIGNAL = ("technician", "tech ", "region", "cities", "city", "sla")
# Jobs per technician per year above which the three-day SLA is at risk / broken.
_AT_RISK_LOAD = 28.0
_CRITICAL_LOAD = 45.0
_OVERSTAFFED_LOAD = 12.0
_OVERSTAFFED_MIN_TEAM = 5


def answer_capacity_question(
    lowered_question: str, employees: list[Employee], service_tickets: list[ServiceTicket]
) -> Optional[ComputedAnswer]:
    """Return the region SLA-capacity answer when the question asks about coverage."""
    if not (mentions_any(lowered_question, _CAPACITY_SIGNAL) and mentions_any(lowered_question, _SCOPE_SIGNAL)):
        return None
    if not employees or not service_tickets:
        return None
    region_rows = _compute_region_capacity(employees, service_tickets)
    critical = [row for row in region_rows if row["severity"] == "critical"]
    at_risk = [row for row in region_rows if row["severity"] == "at_risk"]
    headline = _phrase_answer(len(region_rows), critical, at_risk)
    return ComputedAnswer(
        headline,
        "computed technicians vs job demand per region against the 3-day SLA",
        visualizations.region_map("SLA capacity by region", region_rows),
    )


def _compute_region_capacity(
    employees: list[Employee], service_tickets: list[ServiceTicket]
) -> list[dict]:
    """One row per region: technicians, job demand, load, and an SLA-risk severity."""
    technicians_by_region = Counter(
        employee.region for employee in employees if employee.role == _FIELD_TECHNICIAN_ROLE
    )
    demand_by_region = Counter(
        region_for_city(ticket.city) for ticket in service_tickets if ticket.city
    )
    rows: list[dict] = []
    for region in SERVICE_REGIONS:
        technician_count = technicians_by_region.get(region, 0)
        demand = demand_by_region.get(region, 0)
        load = demand / technician_count if technician_count else float(demand)
        rows.append({
            "region": region,
            "techs": technician_count,
            "demand": demand,
            "load": round(load, 1),
            "severity": _classify_severity(technician_count, load),
        })
    return rows


def _classify_severity(technician_count: int, load: float) -> str:
    """Rate a region's ability to hold the three-day SLA from its technicians-vs-demand load."""
    if technician_count == 0:
        return "critical"
    if load >= _CRITICAL_LOAD:
        return "critical"
    if load >= _AT_RISK_LOAD:
        return "at_risk"
    if technician_count >= _OVERSTAFFED_MIN_TEAM and load < _OVERSTAFFED_LOAD:
        return "over"
    return "ok"


def _phrase_answer(region_count: int, critical: list[dict], at_risk: list[dict]) -> str:
    """A one-line verdict naming the regions that cannot hold the SLA."""
    if not critical and not at_risk:
        return "Every region can hold the 3-day SLA at current staffing."
    named = ", ".join(f"{row['region']} ({row['techs']} tech vs ~{row['demand']} jobs)" for row in critical)
    stretched = ", ".join(row["region"] for row in at_risk)
    parts = [f"{len(critical)} of {region_count} regions can't hold the 3-working-day SLA — {named}."]
    if at_risk:
        parts.append(f"{len(at_risk)} more are stretched ({stretched}).")
    parts.append("It's a distribution problem: total headcount is fine, but technicians aren't where the demand is.")
    return " ".join(parts)
