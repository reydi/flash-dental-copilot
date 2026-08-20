"""Build Flash Dental's employee directory and the people-domain documents.

Single responsibility: expand the declarative ROLE_DIRECTORY into a realistic list
of named staff (deterministic under a seed), and author the org documents the
copilot retrieves for role and business-flow questions. Kept apart from the corpus
generator so each file has one job.
"""
from __future__ import annotations

import random

from scripts.org_entities import (
    CANONICAL_ORG_DOCUMENTS,
    GIVEN_NAMES,
    ROLE_DIRECTORY,
    SERVICE_REGIONS,
    SURNAMES,
)


def _shuffled_unique_names(random_generator: random.Random, already_used: set) -> list[str]:
    """Every given+surname combination, shuffled, minus names already taken."""
    all_combinations = [
        f"{given_name} {surname}" for given_name in GIVEN_NAMES for surname in SURNAMES
    ]
    random_generator.shuffle(all_combinations)
    return [name for name in all_combinations if name not in already_used]


def build_employee_directory(
    random_generator: random.Random, field_technician_names: list[str]
) -> list[dict]:
    """One directory row per person: id, name, role, region — deterministic under the seed."""
    used_names = set(field_technician_names)
    synthesised_name_pool = _shuffled_unique_names(random_generator, used_names)
    next_synthesised_index = 0
    directory: list[dict] = []
    for role_title, _responsibility, headcount, source in ROLE_DIRECTORY:
        for position in range(headcount):
            if source == "field_technicians":
                full_name = field_technician_names[position % len(field_technician_names)]
            else:
                full_name = synthesised_name_pool[next_synthesised_index]
                next_synthesised_index += 1
            region = (
                "Jabodetabek" if role_title == "Executive"
                else random_generator.choice(SERVICE_REGIONS)
            )
            directory.append({
                "employee_id": f"EMP-{len(directory) + 1:04d}",
                "full_name": full_name,
                "role": role_title,
                "region": region,
            })
    return directory


def _headcount_summary_sentence() -> str:
    """A readable "24 Field Technicians, 26 Service Coordinators, …" roll-up."""
    parts = [f"{headcount} {role_title}s" for role_title, _r, headcount, _s in ROLE_DIRECTORY]
    total = sum(headcount for _t, _r, headcount, _s in ROLE_DIRECTORY)
    return f"Flash Dental headcount is {total} people: " + ", ".join(parts) + "."


def build_people_domain_documents() -> list[dict]:
    """Org and role documents folded into the people (technician) domain corpus."""
    headcount_document = {
        "document_id": "org_headcount",
        "category": "overview",
        "text": _headcount_summary_sentence()
        + " Field Technicians are the field team; the rest run the coordination, parts, "
          "sales, finance, and support flow around them.",
    }
    return CANONICAL_ORG_DOCUMENTS + [headcount_document]
