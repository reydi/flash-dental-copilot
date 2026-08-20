"""Re-rank retrieved documents by the question's intent before grounding.

Single responsibility: a light, honest re-rank — when a question is clearly about a
sale ("who sold X", "when was it purchased"), prefer the invoice document over an
equally-matching service log. Only the ORDER changes; each document keeps its true
similarity score, so the abstain gate stays honest.
"""
from __future__ import annotations

from flash_dental_copilot.retrieval import RankedDocument

# Words that mark a question as being about the sale / purchase of a unit.
_SALES_INTENT_WORDS = ("sold", "sell", "sale", "purchase", "bought", "invoice", "sales rep")
# How much to prefer a document category when the intent matches it.
_INTENT_CATEGORY_BOOST = {"invoice": 1.6}


def reorder_by_intent(
    question: str, ranked_documents: list[RankedDocument]
) -> list[RankedDocument]:
    """Return the ranking re-ordered to prefer the category the question's intent wants."""
    lowered_question = question.lower()
    if not any(word in lowered_question for word in _SALES_INTENT_WORDS):
        return ranked_documents
    return sorted(
        ranked_documents,
        key=lambda document: document.similarity_score
        * _INTENT_CATEGORY_BOOST.get(document.category, 1.0),
        reverse=True,
    )
