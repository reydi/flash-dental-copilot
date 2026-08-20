"""Route people/org headcount questions to a computed answer with a breakdown chart.

Single responsibility: recognise "how many <role>" / "how many people" questions and
answer them from the employee directory — computed, never invented.
"""
from __future__ import annotations

from typing import Optional

from flash_dental_copilot import visualizations
from flash_dental_copilot.analytics_common import ComputedAnswer, mentions_any
from flash_dental_copilot.employee_records import (
    Employee,
    count_employees_by_role,
    count_employees_in_role,
)

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


def answer_headcount_question(
    lowered_question: str, employees: list[Employee]
) -> Optional[ComputedAnswer]:
    """Count people by role, or in total, when the question asks how many staff there are."""
    if not employees or not mentions_any(lowered_question, _HEADCOUNT_WORDS):
        return None
    breakdown = count_employees_by_role(employees)
    role_title = _resolve_role(lowered_question)
    if role_title is not None:
        role_count = count_employees_in_role(employees, role_title)
        return ComputedAnswer(
            f"Flash Dental has {role_count} {role_title}s.",
            "counted from the employee directory",
            visualizations.bar_chart("Headcount by role", breakdown, "people", highlight=role_title),
        )
    if mentions_any(lowered_question, _PEOPLE_WORDS):
        return ComputedAnswer(
            f"Flash Dental has {len(employees)} employees across all roles.",
            "counted the employee directory",
            visualizations.bar_chart("Headcount by role", breakdown, "people"),
        )
    return None


def _resolve_role(lowered_question: str) -> Optional[str]:
    """The directory role a question names, or None if it names no role."""
    for keyword, role_title in _ROLE_KEYWORDS.items():
        if keyword in lowered_question:
            return role_title
    return None
