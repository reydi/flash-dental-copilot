"""Route an analytical question to a computed answer, or defer to retrieval.

Single responsibility: recognise the handful of aggregate questions a cockpit
answers by *computing* (counts, rankings), phrase the computed result, and return
None when the question is a factual lookup that document retrieval should handle.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from flash_dental_copilot import structured_analytics
from flash_dental_copilot.kpi_computation import ServiceTicket
from flash_dental_copilot.structured_analytics import MaintenanceRecord

# Words in the question that name a job category, mapped to the ticket's category value.
_JOB_CATEGORY_KEYWORDS = {
    "service": "service",
    "maintenance": "maintenance",
    "install": "installation",
    "installation": "installation",
    "survey": "survey",
    "training": "training",
}
_OVERDUE_WORDS = ("overdue", "delayed", "late", "past due")
_WORST_WORDS = ("least", "worst", "lowest", "underperform", "bottom")
_BEST_WORDS = ("best", "top", "highest", "busiest", "most")


@dataclass(frozen=True)
class ComputedAnswer:
    """An answer the copilot computed by code, with how it was computed."""
    answer_text: str
    computation_detail: str


def answer_analytical_question(
    question: str,
    service_tickets: list[ServiceTicket],
    maintenance_schedule: list[MaintenanceRecord],
) -> Optional[ComputedAnswer]:
    """Return a computed answer for an aggregate question, or None to defer to retrieval."""
    lowered_question = question.lower()

    if "maintenance" in lowered_question and _mentions_any(lowered_question, _OVERDUE_WORDS):
        overdue_count = structured_analytics.count_overdue_maintenance(maintenance_schedule)
        return ComputedAnswer(
            f"{overdue_count} units are overdue for preventive maintenance.",
            "counted from the maintenance schedule",
        )

    if _asks_about_technician(lowered_question) and _mentions_any(lowered_question, _WORST_WORDS):
        ranked = structured_analytics.rank_technicians_by_first_time_fix(service_tickets)
        name, rate = ranked[-1]
        return ComputedAnswer(
            f"{name} has the lowest first-time-fix this period, at {rate}%.",
            "ranked technicians by computed first-time-fix",
        )

    if _asks_about_technician(lowered_question) and _mentions_any(lowered_question, _BEST_WORDS):
        ranked = structured_analytics.rank_technicians_by_first_time_fix(service_tickets)
        name, rate = ranked[0]
        return ComputedAnswer(
            f"{name} leads on first-time-fix this period, at {rate}%.",
            "ranked technicians by computed first-time-fix",
        )

    if "how many" in lowered_question and "outstanding" in lowered_question:
        outstanding_count = sum(
            1 for ticket in service_tickets if ticket.status not in ("finished", "cancelled")
        )
        return ComputedAnswer(
            f"{outstanding_count} jobs are currently outstanding.",
            "counted open service tickets",
        )

    if "how many" in lowered_question and _mentions_any(lowered_question, _JOB_CATEGORY_KEYWORDS):
        categories = {
            category
            for keyword, category in _JOB_CATEGORY_KEYWORDS.items()
            if keyword in lowered_question
        }
        job_count = structured_analytics.count_jobs_in_categories(service_tickets, categories)
        readable_categories = " and ".join(sorted(categories))
        return ComputedAnswer(
            f"{job_count} {readable_categories} jobs in the period.",
            "counted from the service tickets",
        )

    return None


def _mentions_any(text: str, keywords) -> bool:
    return any(keyword in text for keyword in keywords)


def _asks_about_technician(text: str) -> bool:
    return "technician" in text or "who" in text
