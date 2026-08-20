"""Compute the operational dashboard questions from the brief: reliability, blocked
tickets, maintenance compliance, and technician backlog.

Single responsibility: recognise these four aggregate questions, compute each from the
service tickets or the maintenance schedule, and phrase the result with a chart.
"""
from __future__ import annotations

from typing import Optional

from flash_dental_copilot import structured_analytics, visualizations
from flash_dental_copilot.analytics_common import ComputedAnswer, mentions_any
from flash_dental_copilot.kpi_computation import ServiceTicket
from flash_dental_copilot.structured_analytics import MaintenanceRecord

_RELIABILITY_WORDS = ("reliab", "repeat", "problematic", "fails most", "fail the most", "breaks", "most problem")
_PRODUCT_WORDS = ("product", "model", "unit", "machine")
_BLOCKED_WORDS = ("waiting", "stuck", "blocked", "held up", "hold")
_PART_WORDS = ("spare", "part")
_COMPLIANCE_WORDS = ("compliance", "on-time", "on time", "on schedule", "kept up")
_BACKLOG_WORDS = ("backlog",)


def answer_operations_question(
    lowered_question: str,
    service_tickets: list[ServiceTicket],
    maintenance_schedule: list[MaintenanceRecord],
) -> Optional[ComputedAnswer]:
    """Return a computed answer for a dashboard question, or None to defer."""
    if mentions_any(lowered_question, _RELIABILITY_WORDS) and mentions_any(lowered_question, _PRODUCT_WORDS):
        return _reliability_answer(service_tickets)
    if mentions_any(lowered_question, _BLOCKED_WORDS) and mentions_any(lowered_question, _PART_WORDS):
        return _blocked_tickets_answer(service_tickets)
    if "maintenance" in lowered_question and mentions_any(lowered_question, _COMPLIANCE_WORDS):
        return _maintenance_compliance_answer(maintenance_schedule)
    if mentions_any(lowered_question, _BACKLOG_WORDS) or (
        "outstanding" in lowered_question and mentions_any(lowered_question, ("technician", "which", "who", "biggest"))
    ):
        return _backlog_answer(service_tickets)
    return None


def _reliability_answer(service_tickets: list[ServiceTicket]) -> Optional[ComputedAnswer]:
    by_model = structured_analytics.count_repeat_service_by_model(service_tickets)
    if not by_model:
        return None
    worst_model, worst_count = by_model[0]
    return ComputedAnswer(
        f"{worst_model} is the least reliable — {worst_count} units came back for a 2nd+ service, the most of any model.",
        "counted units with repeat service, grouped by model",
        visualizations.bar_chart("Repeat service by model", by_model[:6], "units", highlight=worst_model),
    )


def _blocked_tickets_answer(service_tickets: list[ServiceTicket]) -> Optional[ComputedAnswer]:
    by_reason = structured_analytics.count_outstanding_by_hold_reason(service_tickets)
    if not by_reason:
        return None
    spare_part_count = dict(by_reason).get("spare part", 0)
    total_blocked = sum(count for _reason, count in by_reason)
    return ComputedAnswer(
        f"{spare_part_count} open tickets are stuck waiting on a spare part, of {total_blocked} blocked in total.",
        "counted open tickets by what they are blocked on",
        visualizations.bar_chart("Open tickets — blocked on", by_reason, "tickets", highlight="spare part"),
    )


def _maintenance_compliance_answer(schedule: list[MaintenanceRecord]) -> ComputedAnswer:
    rate, on_time, total = structured_analytics.maintenance_compliance(schedule)
    return ComputedAnswer(
        f"On-time maintenance compliance is {rate}% — {on_time} of {total} units on schedule, {total - on_time} overdue.",
        "computed from the maintenance schedule",
        visualizations.stat("On-time maintenance", f"{rate}%", "", f"{on_time} of {total} on schedule"),
    )


def _backlog_answer(service_tickets: list[ServiceTicket]) -> Optional[ComputedAnswer]:
    ranked = structured_analytics.rank_technicians_by_backlog(service_tickets)
    if not ranked:
        return None
    top_name, top_count = ranked[0]
    return ComputedAnswer(
        f"{top_name} has the biggest backlog — {top_count} open tickets.",
        "counted each technician's open tickets",
        visualizations.bar_chart("Backlog by technician (open tickets)", ranked[:6], "open", highlight=top_name),
    )
