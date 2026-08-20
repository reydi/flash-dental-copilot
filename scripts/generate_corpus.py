"""Generate the Flash Dental demo corpus: documents + structured records → JSON.

Single responsibility: orchestrate the declarative entities into a much larger but
still realistic corpus — hundreds of units and tickets, a wider field team, and a
full employee directory — then write the data files the API reads. Deterministic:
a fixed seed means regenerating always produces the same corpus.

Run from the repo root:  python -m scripts.generate_corpus
"""
from __future__ import annotations

import json
import random
from pathlib import Path

from scripts.asset_documents import (
    build_generated_asset_documents,
    build_generated_manual_documents,
    build_unit_registry,
    generate_unit_serial,
)
from scripts.corpus_entities import (
    ASSET_PRESET_QUESTIONS,
    CANONICAL_ASSET_DOCUMENTS,
    CANONICAL_TECHNICIAN_DOCUMENTS,
    FIELD_TECHNICIANS,
    TECHNICIAN_PRESET_QUESTIONS,
)
from scripts.employee_directory import (
    build_employee_directory,
    build_people_domain_documents,
)
from scripts.org_entities import ORG_PRESET_QUESTIONS

DATA_DIRECTORY = (
    Path(__file__).resolve().parent.parent / "flash_dental_copilot" / "data"
)
GENERATED_UNIT_COUNT = 240
SERVICE_TICKET_COUNT = 520
OUTSTANDING_JOB_COUNT = 18
OVERDUE_MAINTENANCE_COUNT = 46
RANDOM_SEED = 1042

# Ticket volume per technician: the five flagship names carry more; the wider team
# each gets a steady share, enough finished jobs for a stable, comparable rate.
FLAGSHIP_TICKET_WEIGHTS = [18, 13, 10, 8, 6]
OTHER_TECHNICIAN_WEIGHT = 7
TECHNICIAN_TICKET_WEIGHTS = FLAGSHIP_TICKET_WEIGHTS + [OTHER_TECHNICIAN_WEIGHT] * (
    len(FIELD_TECHNICIANS) - len(FLAGSHIP_TICKET_WEIGHTS)
)

# Miss one first-time-fix in every N finished jobs — distinct for the flagship five so
# their ranking is meaningful; the wider team defaults high, so Arman stays the lowest.
FIRST_TIME_FIX_MISS_EVERY = {
    "Yudi Pratama": 8,
    "Dedi Kurniawan": 6,
    "Febri Santoso": 5,
    "Arga Wibowo": 4,
    "Arman Hakim": 3,
}
DEFAULT_MISS_EVERY = 5
JOB_CATEGORIES = ["service", "maintenance", "installation", "survey", "training"]
JOB_CATEGORY_WEIGHTS = [40, 30, 14, 9, 7]


def build_generated_technician_documents() -> list[dict]:
    """A monthly log for each remaining flagship technician beyond the canonical two."""
    monthly_job_counts = {"Febri Santoso": 8, "Arga Wibowo": 5, "Arman Hakim": 3}
    return [
        {
            "document_id": f"tech_{full_name.split()[0].lower()}_june",
            "category": "monthly_log",
            "text": (
                f"Technician {full_name} June log: closed {job_count} jobs, "
                f"mostly Jabodetabek service and scheduled maintenance."
            ),
        }
        for full_name, job_count in monthly_job_counts.items()
    ]


def build_service_tickets(
    random_generator: random.Random, serial_to_clinic: dict[str, tuple[str, str]]
) -> list[dict]:
    """Structured tickets: per-technician first-time-fix, a job category, and the clinic served."""
    tickets: list[dict] = []
    finished_jobs_per_technician: dict[str, int] = {}
    for sequence_number in range(1, SERVICE_TICKET_COUNT + 1):
        unit_serial = generate_unit_serial((sequence_number % GENERATED_UNIT_COUNT) + 1)
        clinic_name, city = serial_to_clinic.get(unit_serial, ("", ""))
        technician_name = random_generator.choices(
            FIELD_TECHNICIANS, weights=TECHNICIAN_TICKET_WEIGHTS, k=1
        )[0]
        is_outstanding = sequence_number <= OUTSTANDING_JOB_COUNT
        finished_index = finished_jobs_per_technician.get(technician_name, 0)
        miss_every = FIRST_TIME_FIX_MISS_EVERY.get(technician_name, DEFAULT_MISS_EVERY)
        was_fixed_first_visit = not is_outstanding and finished_index % miss_every != 0
        if not is_outstanding:
            finished_jobs_per_technician[technician_name] = finished_index + 1
        tickets.append({
            "ticket_id": f"TKT-{sequence_number:04d}",
            "unit_serial": unit_serial,
            "technician_name": technician_name,
            "was_fixed_first_visit": was_fixed_first_visit,
            "cycle_time_days": random_generator.randint(2, 17),
            "status": "outstanding" if is_outstanding else "finished",
            "job_category": random_generator.choices(JOB_CATEGORIES, weights=JOB_CATEGORY_WEIGHTS, k=1)[0],
            "clinic_name": clinic_name,
            "city": city,
        })
    return tickets


def build_maintenance_schedule(random_generator: random.Random) -> list[dict]:
    """One preventive-maintenance record per unit, a fixed number already overdue."""
    schedule: list[dict] = []
    for sequence_number in range(1, GENERATED_UNIT_COUNT + 1):
        is_overdue = sequence_number <= OVERDUE_MAINTENANCE_COUNT
        due_month = random_generator.randint(1, 12)
        due_year = 2025 if is_overdue else 2026
        schedule.append({
            "unit_serial": generate_unit_serial(sequence_number),
            "next_maintenance_due": f"{due_year}-{due_month:02d}-15",
            "is_overdue": is_overdue,
        })
    return schedule


def write_json_file(filename: str, payload) -> None:
    """Write one data file, pretty-printed and UTF-8, keeping Unicode readable."""
    destination = DATA_DIRECTORY / filename
    destination.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )


def main() -> None:
    """Generate every data file the API reads."""
    DATA_DIRECTORY.mkdir(parents=True, exist_ok=True)
    random_generator = random.Random(RANDOM_SEED)
    employee_directory = build_employee_directory(random_generator, FIELD_TECHNICIANS)
    sales_representative_names = [
        employee["full_name"]
        for employee in employee_directory
        if employee["role"] == "Sales Representative"
    ]
    unit_registry = build_unit_registry(random_generator, GENERATED_UNIT_COUNT)
    serial_to_clinic = {
        unit["serial"]: (unit["clinic_name"], unit["city"]) for unit in unit_registry
    }
    asset_documents = (
        CANONICAL_ASSET_DOCUMENTS
        + build_generated_manual_documents()
        + build_generated_asset_documents(
            random_generator, unit_registry, sales_representative_names
        )
    )
    technician_documents = (
        CANONICAL_TECHNICIAN_DOCUMENTS
        + build_generated_technician_documents()
        + build_people_domain_documents()
    )
    write_json_file(
        "asset_service_documents.json",
        {"documents": asset_documents, "preset_questions": ASSET_PRESET_QUESTIONS},
    )
    write_json_file(
        "technician_performance_documents.json",
        {
            "documents": technician_documents,
            "preset_questions": TECHNICIAN_PRESET_QUESTIONS + ORG_PRESET_QUESTIONS,
        },
    )
    write_json_file(
        "service_tickets.json", build_service_tickets(random_generator, serial_to_clinic)
    )
    write_json_file("maintenance_schedule.json", build_maintenance_schedule(random_generator))
    write_json_file("employees.json", employee_directory)
    write_json_file("units.json", unit_registry)
    print(
        f"Wrote {len(asset_documents)} asset documents, "
        f"{len(technician_documents)} technician/org documents, "
        f"{SERVICE_TICKET_COUNT} service tickets, {GENERATED_UNIT_COUNT} units + maintenance records, "
        f"and {len(employee_directory)} employees to {DATA_DIRECTORY}."
    )


if __name__ == "__main__":
    main()
