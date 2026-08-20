"""Shared pieces for the analytical-question routers: the answer type and a text helper.

Single responsibility: the small vocabulary two routers (ticket/maintenance analytics
and people/org analytics) both depend on, kept here so neither imports the other.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ComputedAnswer:
    """An answer the copilot computed by code, with how it was computed and an optional chart."""
    answer_text: str
    computation_detail: str
    visualization: Optional[dict] = None


def mentions_any(text: str, keywords) -> bool:
    """True when any keyword appears in the text."""
    return any(keyword in text for keyword in keywords)
