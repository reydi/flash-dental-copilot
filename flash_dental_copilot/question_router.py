"""Route an analytical question to a computed answer, or defer to retrieval.

Single responsibility: recognise the aggregate questions a cockpit answers by
*computing* (counts, rankings, per-technician clinic lists) over the service tickets
and maintenance schedule, phrase the result with a chart, and return None when the
question is a factual lookup that document retrieval (or people_questions) should handle.
"""
from __future__ import annotations

from typing import Optional

from flash_dental_copilot import structured_analytics, visualizations
from flash_dental_copilot.analytics_common import ComputedAnswer, mentions_any
from flash_dental_copilot.employee_records import Employee
from flash_dental_copilot.kpi_computation import ServiceTicket
from flash_dental_copilot.people_questions import answer_headcount_question
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
# A ranking question must actually be about technician performance — not just any "who".
_TECH_PERF_WORDS = ("technician", "tech ", "first-time-fix", "first time fix", "fix rate", "performer", "performing")
# Words that ask which clinics/customers a technician served.
_CLINIC_LIST_WORDS = ("clinic", "doctor", "handled", "serviced", "visited", "customer", "which units")


def answer_analytical_question(
    question: str,
    service_tickets: list[ServiceTicket],
    maintenance_schedule: list[MaintenanceRecord],
    employees: Optional[list[Employee]] = None,
) -> Optional[ComputedAnswer]:
    """Return a computed answer for an aggregate question, or None to defer to retrieval."""
    lowered_question = question.lower()

    headcount_answer = answer_headcount_question(lowered_question, employees or [])
    if headcount_answer is not None:
        return headcount_answer

    if "maintenance" in lowered_question and mentions_any(lowered_question, _OVERDUE_WORDS):
        overdue_count = structured_analytics.count_overdue_maintenance(maintenance_schedule)
        return ComputedAnswer(
            f"{overdue_count} units are overdue for preventive maintenance.",
            "counted from the maintenance schedule",
            visualizations.stat(
                "Overdue maintenance", overdue_count, "units",
                f"of {len(maintenance_schedule)} units on the schedule",
            ),
        )

    clinics_answer = _answer_clinics_for_technician(lowered_question, service_tickets)
    if clinics_answer is not None:
        return clinics_answer

    if mentions_any(lowered_question, _TECH_PERF_WORDS) and mentions_any(lowered_question, _WORST_WORDS):
        ranked = structured_analytics.rank_technicians_by_first_time_fix(service_tickets)
        name, _rate = ranked[-1]
        return ComputedAnswer(
            f"{name} has the lowest first-time-fix this period, at {_rate}%.",
            "ranked technicians by computed first-time-fix",
            visualizations.bar_chart("Lowest first-time-fix (worst 6)", ranked[-6:], "%", highlight=name),
        )

    if mentions_any(lowered_question, _TECH_PERF_WORDS) and mentions_any(lowered_question, _BEST_WORDS):
        ranked = structured_analytics.rank_technicians_by_first_time_fix(service_tickets)
        name, _rate = ranked[0]
        return ComputedAnswer(
            f"{name} leads on first-time-fix this period, at {_rate}%.",
            "ranked technicians by computed first-time-fix",
            visualizations.bar_chart("Top first-time-fix (best 6)", ranked[:6], "%", highlight=name),
        )

    if "how many" in lowered_question and "outstanding" in lowered_question:
        outstanding_count = sum(
            1 for ticket in service_tickets if ticket.status not in ("finished", "cancelled")
        )
        return ComputedAnswer(
            f"{outstanding_count} jobs are currently outstanding.",
            "counted open service tickets",
            visualizations.stat("Outstanding jobs", outstanding_count, "open", "not yet finished"),
        )

    if "how many" in lowered_question and mentions_any(lowered_question, _JOB_CATEGORY_KEYWORDS):
        categories = {
            category
            for keyword, category in _JOB_CATEGORY_KEYWORDS.items()
            if keyword in lowered_question
        }
        job_count = structured_analytics.count_jobs_in_categories(service_tickets, categories)
        readable_categories = " and ".join(sorted(categories))
        counts_by_category = structured_analytics.count_jobs_by_category(service_tickets)
        chart_items = [(category, counts_by_category.get(category, 0)) for category in sorted(categories)]
        return ComputedAnswer(
            f"{job_count} {readable_categories} jobs in the period.",
            "counted from the service tickets",
            visualizations.bar_chart("Jobs by category", chart_items, "jobs"),
        )

    return None


def _answer_clinics_for_technician(
    lowered_question: str, service_tickets: list[ServiceTicket]
) -> Optional[ComputedAnswer]:
    """List the clinics a named technician has serviced, when the question asks for them."""
    if not mentions_any(lowered_question, _CLINIC_LIST_WORDS):
        return None
    technician_name = _named_technician(lowered_question, service_tickets)
    if technician_name is None:
        return None
    clinics = structured_analytics.list_clinics_for_technician(service_tickets, technician_name)
    if not clinics:
        return None
    given_name = technician_name.split()[0]
    preview = ", ".join(clinic for clinic, _city in clinics[:3])
    return ComputedAnswer(
        f"{given_name} serviced {len(clinics)} clinics this period — including {preview}.",
        "joined the technician's tickets to the clinics they serviced",
        visualizations.list_cards(f"Clinics {given_name} serviced", clinics),
    )


def _named_technician(lowered_question: str, service_tickets: list[ServiceTicket]) -> Optional[str]:
    """The technician a question names by given name, matched against the ticket roster."""
    for technician_name in {ticket.technician_name for ticket in service_tickets}:
        if technician_name.split()[0].lower() in lowered_question:
            return technician_name
    return None
