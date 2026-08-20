"""Route an analytical question to a computed answer, or defer to retrieval.

Single responsibility: recognise the handful of aggregate questions a cockpit
answers by *computing* (counts, rankings), phrase the computed result, and return
None when the question is a factual lookup that document retrieval should handle.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from flash_dental_copilot import structured_analytics
from flash_dental_copilot.employee_records import Employee, count_employees_in_role
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
_HEADCOUNT_WORDS = ("how many", "number of", "count of", "headcount")
_PEOPLE_WORDS = ("employee", "people", "staff", "headcount", "work at")
# A role word in the question, mapped to its directory role title.
_ROLE_KEYWORDS = {
    "technician": "Field Technician",
    "coordinator": "Service Coordinator",
    "warehouse": "Warehouse / Parts Officer",
    "parts": "Warehouse / Parts Officer",
    "sales": "Sales Representative",
    "manager": "Service Manager",
    "finance": "Finance Officer",
    "support": "Customer Support Agent",
    "admin": "Regional Admin",
    "executive": "Executive",
}


@dataclass(frozen=True)
class ComputedAnswer:
    """An answer the copilot computed by code, with how it was computed."""
    answer_text: str
    computation_detail: str


def answer_analytical_question(
    question: str,
    service_tickets: list[ServiceTicket],
    maintenance_schedule: list[MaintenanceRecord],
    employees: Optional[list[Employee]] = None,
) -> Optional[ComputedAnswer]:
    """Return a computed answer for an aggregate question, or None to defer to retrieval."""
    lowered_question = question.lower()

    headcount_answer = _answer_headcount_question(lowered_question, employees or [])
    if headcount_answer is not None:
        return headcount_answer

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


def _answer_headcount_question(
    lowered_question: str, employees: list[Employee]
) -> Optional[ComputedAnswer]:
    """Count people by role, or in total, when the question asks how many staff there are."""
    if not employees or not _mentions_any(lowered_question, _HEADCOUNT_WORDS):
        return None
    role_title = _resolve_role(lowered_question)
    if role_title is not None:
        role_count = count_employees_in_role(employees, role_title)
        return ComputedAnswer(
            f"Flash Dental has {role_count} {role_title}s.",
            "counted from the employee directory",
        )
    if _mentions_any(lowered_question, _PEOPLE_WORDS):
        return ComputedAnswer(
            f"Flash Dental has {len(employees)} employees across all roles.",
            "counted the employee directory",
        )
    return None


def _resolve_role(lowered_question: str) -> Optional[str]:
    """The directory role a question names, or None if it names no role."""
    for keyword, role_title in _ROLE_KEYWORDS.items():
        if keyword in lowered_question:
            return role_title
    return None


def _mentions_any(text: str, keywords) -> bool:
    return any(keyword in text for keyword in keywords)


def _asks_about_technician(text: str) -> bool:
    return "technician" in text or "who" in text
