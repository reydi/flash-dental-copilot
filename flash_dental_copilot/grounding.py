"""Grounding gate: decide whether the top-ranked document is a trustworthy answer.

Single responsibility: turn a ranked list into either a grounded, cited answer
or an explicit abstention. The copilot must refuse rather than invent — a wrong
answer destroys the trust the whole cockpit depends on.
"""
from __future__ import annotations

from dataclasses import dataclass

from flash_dental_copilot.retrieval import RankedDocument

# Below this cosine similarity the best match is too weak to trust; abstain instead.
# Set deliberately high: a confident wrong answer is worse than an honest "not in our records".
ABSTAIN_SIMILARITY_THRESHOLD = 0.16


@dataclass(frozen=True)
class GroundedAnswer:
    """The copilot's verdict: either a cited answer, or an honest abstention."""
    abstained: bool
    similarity_score: float
    answer_text: str
    citation_document_id: str | None


def select_grounded_answer(ranked_documents: list[RankedDocument]) -> GroundedAnswer:
    """Return the top document as a cited answer, or abstain when it is too weak."""
    best_match = ranked_documents[0] if ranked_documents else None
    if best_match is None or best_match.similarity_score < ABSTAIN_SIMILARITY_THRESHOLD:
        best_score = best_match.similarity_score if best_match else 0.0
        return GroundedAnswer(
            abstained=True,
            similarity_score=best_score,
            answer_text="Not in our records — I don't have a grounded answer for that.",
            citation_document_id=None,
        )
    return GroundedAnswer(
        abstained=False,
        similarity_score=best_match.similarity_score,
        answer_text=best_match.text,
        citation_document_id=best_match.document_id,
    )
