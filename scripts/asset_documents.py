"""Build the generated asset-domain documents: a service log + invoice per unit.

Single responsibility: expand the unit/clinic/fault vocabulary into per-unit service
logs and sales invoices (each naming a real sales rep, purchase date, and price), plus
a short troubleshooting manual per fault. Deterministic under the generator's seed.
"""
from __future__ import annotations

import random

from scripts.corpus_entities import DENTAL_CLINICS, FAULT_SYMPTOMS, SERVICE_MODELS


def generate_unit_serial(sequence_number: int) -> str:
    """A realistic EX9-format serial, e.g. EX92026030007."""
    return f"EX9202603{sequence_number:04d}"


def build_unit_registry(random_generator: random.Random, unit_count: int) -> list[dict]:
    """Assign each unit its model, clinic, and city once — shared by docs and tickets."""
    return [
        {
            "serial": generate_unit_serial(sequence_number),
            "model": random_generator.choice(SERVICE_MODELS),
            "clinic_name": (clinic := random_generator.choice(DENTAL_CLINICS))[0],
            "city": clinic[1],
        }
        for sequence_number in range(1, unit_count + 1)
    ]


def build_generated_asset_documents(
    random_generator: random.Random, unit_registry: list[dict], sales_representative_names: list[str]
) -> list[dict]:
    """One service-log document per registered unit, plus a matching, sales-attributed invoice."""
    generated_documents: list[dict] = []
    for unit in unit_registry:
        unit_serial, model, clinic_name, city = (
            unit["serial"], unit["model"], unit["clinic_name"], unit["city"]
        )
        complaint, spare_part, _root_cause = random_generator.choice(FAULT_SYMPTOMS)
        sales_representative = random_generator.choice(sales_representative_names)
        purchase_year = random_generator.choice([2021, 2022, 2023, 2024])
        purchase_month = random_generator.randint(1, 12)
        price_millions = random_generator.choice([65, 72, 78, 85, 92, 110, 140])
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
                f"Sales invoice for dental unit {unit_serial} (model {model}): "
                f"sold by sales rep {sales_representative}, purchased "
                f"{purchase_year}-{purchase_month:02d} for Rp {price_millions},000,000, "
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
