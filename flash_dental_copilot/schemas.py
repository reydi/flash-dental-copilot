"""Request and response models for the copilot HTTP API.

Single responsibility: the shape of what crosses the wire, validated by pydantic.
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    """A plain-language question, scoped to one domain."""
    question: str = Field(min_length=1, max_length=500)
    domain: str = Field(default="assets")


class AskResponse(BaseModel):
    """A computed, retrieved, or abstained answer — with its citation and KPIs."""
    domain: str
    question: str
    answer_kind: str  # "computed" (aggregate), "retrieved" (grounded lookup), or "abstained"
    abstained: bool
    similarity_score: float
    answer_text: str
    citation_document_id: Optional[str]
    computation_detail: Optional[str]
    kpi_summary: str
    pii_masking_example: str
    computed_by_code_note: str
