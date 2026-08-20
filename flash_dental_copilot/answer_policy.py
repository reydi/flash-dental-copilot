"""Answer-policy guards for the API edge: refuse private data, decorate flow answers.

Single responsibility: the two small policy decisions /ask makes beyond retrieval —
whether a question asks for someone's private contact data (refused, never retrieved),
and whether a retrieved answer warrants the end-to-end service-flow diagram.
"""
from __future__ import annotations

from typing import Optional

from flash_dental_copilot.visualizations import business_flow_diagram

# Questions asking for a person's private contact data — refused, never retrieved.
_SENSITIVE_PERSONAL_TERMS = (
    "home address", "address", "phone", "salary", "date of birth", "personal number",
    "national id", "ktp", "nik", "bank account", "home number", "personal contact",
)
# Retrieval citations that warrant showing the end-to-end service flow diagram.
_FLOW_CITATIONS = ("org_business_flow", "role_service_coordinator", "role_customer_support")

REFUSAL_TEXT = (
    "Not in our records — personal contact details (home address, phone, salary) aren't "
    "stored in the service data. Even if they were, they'd be access-controlled by role, "
    "not answerable here."
)


def asks_for_sensitive_personal_data(question: str) -> bool:
    """True when the question asks for private contact/PII about a person."""
    lowered = question.lower()
    return any(term in lowered for term in _SENSITIVE_PERSONAL_TERMS)


def visualization_for_citation(citation_document_id: Optional[str]) -> Optional[dict]:
    """Attach the service-flow diagram when a retrieved answer is about how work moves."""
    if citation_document_id in _FLOW_CITATIONS:
        return business_flow_diagram()
    return None
