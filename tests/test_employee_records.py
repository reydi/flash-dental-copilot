"""Tests for the employee directory: role counts and loading the real directory."""
from __future__ import annotations

from flash_dental_copilot.employee_records import (
    Employee,
    count_employees_in_role,
    load_employees,
)


def test_count_employees_in_role_counts_only_that_role():
    people = [
        Employee("E1", "A", "Field Technician", "X"),
        Employee("E2", "B", "Sales Representative", "Y"),
        Employee("E3", "C", "Field Technician", "Z"),
    ]
    assert count_employees_in_role(people, "Field Technician") == 2
    assert count_employees_in_role(people, "Finance Officer") == 0


def test_directory_loads_hundreds_of_people_across_the_business_roles():
    employees = load_employees()
    assert len(employees) > 100
    roles = {employee.role for employee in employees}
    for expected_role in ("Field Technician", "Service Coordinator", "Warehouse / Parts Officer", "Sales Representative"):
        assert expected_role in roles
