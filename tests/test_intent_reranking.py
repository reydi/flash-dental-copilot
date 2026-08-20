"""Tests for intent-based re-ranking: a 'who sold' question prefers the invoice."""
from __future__ import annotations

from flash_dental_copilot.intent_reranking import reorder_by_intent
from flash_dental_copilot.retrieval import RankedDocument


def _ranked(document_id: str, category: str, similarity_score: float) -> RankedDocument:
    return RankedDocument(document_id, category, "", similarity_score)


def test_sales_intent_prefers_invoice_over_a_higher_scoring_service_log():
    ranking = [_ranked("log", "service_log", 0.41), _ranked("inv", "invoice", 0.40)]
    reordered = reorder_by_intent("who sold this unit and when was it purchased", ranking)
    assert reordered[0].document_id == "inv"
    # the invoice keeps its true score — the boost only re-orders, it doesn't inflate.
    assert reordered[0].similarity_score == 0.40


def test_non_sales_intent_leaves_the_order_unchanged():
    ranking = [_ranked("log", "service_log", 0.41), _ranked("inv", "invoice", 0.40)]
    reordered = reorder_by_intent("show its service history", ranking)
    assert reordered[0].document_id == "log"
