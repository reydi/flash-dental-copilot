"""Generate the Flash Dental demo corpus: documents + structured tickets → JSON.

Single responsibility: expand the declarative entities into a much larger but
still realistic corpus and write the three data files the API reads. Deterministic
— a fixed seed means regenerating always produces the same corpus.

Run from the repo root:  python -m scripts.generate_corpus
"""
from __future__ import annotations

import json
import random
from pathlib import Path

from scripts.corpus_entities import (
    ASSET_PRESET_QUESTIONS,
    CANONICAL_ASSET_DOCUMENTS,
    CANONICAL_TECHNICIAN_DOCUMENTS,
    DENTAL_CLINICS,
    FAULT_SYMPTOMS,
    FIELD_TECHNICIANS,
    SERVICE_MODELS,
    TECHNICIAN_PRESET_QUESTIONS,
)

DATA_DIRECTORY = (
    Path(__file__).resolve().parent.parent / "flash_dental_copilot" / "data"
)
GENERATED_UNIT_COUNT = 34
SERVICE_TICKET_COUNT = 120
OUTSTANDING_JOB_COUNT = 7
RANDOM_SEED = 1042


def generate_unit_serial(sequence_number: int) -> str:
    """A realistic EX9-format serial, e.g. EX92026030007."""
    return f"EX9202603{sequence_number:04d}"


def build_generated_asset_documents(random_generator: random.Random) -> list[dict]:
    """One service-log document per generated unit, plus a matching invoice each."""
    generated_documents: list[dict] = []
    for sequence_number in range(1, GENERATED_UNIT_COUNT + 1):
        unit_serial = generate_unit_serial(sequence_number)
        model = random_generator.choice(SERVICE_MODELS)
        clinic_name, city = random_generator.choice(DENTAL_CLINICS)
        complaint, spare_part, _root_cause = random_generator.choice(FAULT_SYMPTOMS)
        generated_documents.append({
            "document_id": f"service_log_{unit_serial}",
            "category": "service_log",
            "text": (
                f"Dental unit {unit_serial} (model {model}) at {clinic_name}, {city}. "
                f"Reported {complaint}; replaced the {spare_part}; resolved on the visit."
            ),
        })
        generated_documents.append({
            "document_id": f"invoice_{unit_serial}",
            "category": "invoice",
            "text": (
                f"Sales invoice for dental unit {unit_serial} (model {model}), "
                f"installed at {clinic_name}, {city}."
            ),
        })
    return generated_documents


def build_generated_manual_documents() -> list[dict]:
    """A short troubleshooting manual entry per fault symptom."""
    return [
        {
            "document_id": f"manual_{spare_part.replace(' ', '_')}",
            "category": "manual",
            "text": (
                f"Troubleshooting {complaint}: the usual root cause is {root_cause}. "
                f"Inspect and replace the {spare_part} to prevent a repeat visit."
            ),
        }
        for complaint, spare_part, root_cause in FAULT_SYMPTOMS
    ]


def build_generated_technician_documents() -> list[dict]:
    """A monthly log for each remaining technician beyond the canonical two."""
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


# Miss one first-time-fix in every N finished jobs — distinct per technician so
# rankings are meaningful: Yudi ~87%, Dedi ~83%, Febri 80%, Arga 75%, Arman ~67%.
FIRST_TIME_FIX_MISS_EVERY = {
    "Yudi Pratama": 8,
    "Dedi Kurniawan": 6,
    "Febri Santoso": 5,
    "Arga Wibowo": 4,
    "Arman Hakim": 3,
}
# Job categories, weighted toward everyday service and maintenance.
JOB_CATEGORIES = ["service", "maintenance", "installation", "survey", "training"]
JOB_CATEGORY_WEIGHTS = [40, 30, 14, 9, 7]
OVERDUE_MAINTENANCE_COUNT = 9


def build_service_tickets(random_generator: random.Random) -> list[dict]:
    """Structured tickets: distinct per-technician first-time-fix, plus a job category."""
    tickets: list[dict] = []
    finished_jobs_per_technician: dict[str, int] = {}
    for sequence_number in range(1, SERVICE_TICKET_COUNT + 1):
        unit_serial = generate_unit_serial((sequence_number % GENERATED_UNIT_COUNT) + 1)
        technician_name = random_generator.choices(
            FIELD_TECHNICIANS, weights=[16, 10, 8, 5, 3], k=1
        )[0]
        is_outstanding = sequence_number <= OUTSTANDING_JOB_COUNT
        finished_index = finished_jobs_per_technician.get(technician_name, 0)
        miss_every = FIRST_TIME_FIX_MISS_EVERY.get(technician_name, 4)
        was_fixed_first_visit = not is_outstanding and finished_index % miss_every != 0
        if not is_outstanding:
            finished_jobs_per_technician[technician_name] = finished_index + 1
        tickets.append({
            "ticket_id": f"TKT-{sequence_number:04d}",
            "unit_serial": unit_serial,
            "technician_name": technician_name,
            "was_fixed_first_visit": was_fixed_first_visit,
            "cycle_time_days": random_generator.randint(2, 13),
            "status": "outstanding" if is_outstanding else "finished",
            "job_category": random_generator.choices(JOB_CATEGORIES, weights=JOB_CATEGORY_WEIGHTS, k=1)[0],
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
    asset_documents = (
        CANONICAL_ASSET_DOCUMENTS
        + build_generated_manual_documents()
        + build_generated_asset_documents(random_generator)
    )
    technician_documents = (
        CANONICAL_TECHNICIAN_DOCUMENTS + build_generated_technician_documents()
    )
    write_json_file(
        "asset_service_documents.json",
        {"documents": asset_documents, "preset_questions": ASSET_PRESET_QUESTIONS},
    )
    write_json_file(
        "technician_performance_documents.json",
        {"documents": technician_documents, "preset_questions": TECHNICIAN_PRESET_QUESTIONS},
    )
    write_json_file("service_tickets.json", build_service_tickets(random_generator))
    write_json_file("maintenance_schedule.json", build_maintenance_schedule(random_generator))
    print(
        f"Wrote {len(asset_documents)} asset documents, "
        f"{len(technician_documents)} technician documents, "
        f"{SERVICE_TICKET_COUNT} service tickets, and "
        f"{GENERATED_UNIT_COUNT} maintenance records to {DATA_DIRECTORY}."
    )


if __name__ == "__main__":
    main()
