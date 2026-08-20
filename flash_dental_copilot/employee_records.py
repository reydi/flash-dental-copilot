"""Load the employee directory and count staff by role (I/O edge + tiny helpers).

Single responsibility: read employees.json into typed rows and answer the two
questions a cockpit computes over people — how many in a role, and how many in total.
"""
from __future__ import annotations

import json
from dataclasses import dataclass

from flash_dental_copilot.corpus import DATA_DIRECTORY

EMPLOYEES_FILENAME = "employees.json"


@dataclass(frozen=True)
class Employee:
    """One person in the after-sales organisation."""
    employee_id: str
    full_name: str
    role: str
    region: str


def load_employees() -> list[Employee]:
    """Read the employee directory the headcount answers are computed from."""
    employees_file = DATA_DIRECTORY / EMPLOYEES_FILENAME
    raw_employees = json.loads(employees_file.read_text(encoding="utf-8"))
    return [Employee(**employee_fields) for employee_fields in raw_employees]


def count_employees_in_role(employees: list[Employee], role_title: str) -> int:
    """How many people hold the given role."""
    return sum(1 for employee in employees if employee.role == role_title)
