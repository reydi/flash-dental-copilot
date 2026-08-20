"""Tests for the grounding gate: cite a strong match, abstain on a weak one."""
from __future__ import annotations

from flash_dental_copilot.grounding import (
    ABSTAIN_SIMILARITY_THRESHOLD,
    select_grounded_answer,
)
from flash_dental_copilot.retrieval import RankedDocument


def _ranked(document_id: str, similarity_score: float) -> RankedDocument:
    return RankedDocument(
        document_id=document_id,
        category="service_log",
        text=f"text for {document_id}",
        similarity_score=similarity_score,
    )


def test_strong_top_match_becomes_a_cited_answer():
    grounded_answer = select_grounded_answer([_ranked("service_log_FD-1042", 0.9)])
    assert grounded_answer.abstained is False
    assert grounded_answer.citation_document_id == "service_log_FD-1042"
    assert grounded_answer.answer_text == "text for service_log_FD-1042"


def test_weak_top_match_abstains_instead_of_answering():
    weak_score = ABSTAIN_SIMILARITY_THRESHOLD - 0.01
    grounded_answer = select_grounded_answer([_ranked("service_log_FD-1042", weak_score)])
    assert grounded_answer.abstained is True
    assert grounded_answer.citation_document_id is None
    assert "Not in our records" in grounded_answer.answer_text


def test_empty_ranking_abstains():
    grounded_answer = select_grounded_answer([])
    assert grounded_answer.abstained is True
    assert grounded_answer.similarity_score == 0.0
