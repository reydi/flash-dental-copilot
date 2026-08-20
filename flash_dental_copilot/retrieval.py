"""Pure text-retrieval core: rank documents against a plain-language question.

Single responsibility: the transparent TF-IDF + cosine model that turns a
question and a corpus into a relevance-ranked list. No I/O, no framework.

This is the v1 SHAPE. `embed_text_as_tfidf_vector` is the one seam where
production swaps in Vertex AI embeddings — change that function, keep the rest.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass

import snowballstemmer

# Terms that carry no retrieval signal; dropped before scoring.
STOP_WORDS = frozenset({
    "the", "a", "an", "is", "are", "was", "for", "of", "on", "in", "to", "and",
    "or", "with", "at", "by", "be", "this", "that", "our", "your", "what", "how",
    "do", "does", "it", "its", "their", "has", "have", "which", "when", "where",
    "show", "me", "give", "tell", "about",
})

_ALPHANUMERIC_TERM_PATTERN = re.compile(r"[a-z0-9]+")
# Stem so morphological variants collide: fail/fails/failing, goal/goals, unit/units.
_ENGLISH_STEMMER = snowballstemmer.stemmer("english")


@dataclass(frozen=True)
class IndexedDocument:
    """A corpus document with its precomputed TF-IDF vector, ready to score."""
    document_id: str
    category: str
    text: str
    tfidf_vector: dict[str, float]


@dataclass(frozen=True)
class RankedDocument:
    """A document paired with its similarity to the question, in range 0..1."""
    document_id: str
    category: str
    text: str
    similarity_score: float


def tokenize_into_terms(text: str) -> list[str]:
    """Lowercase, split into alphanumeric terms, drop stop-words, and stem the rest."""
    candidate_terms = _ALPHANUMERIC_TERM_PATTERN.findall(text.lower())
    meaningful_terms = [
        term
        for term in candidate_terms
        if len(term) > 1 and term not in STOP_WORDS
    ]
    return _ENGLISH_STEMMER.stemWords(meaningful_terms)


def compute_inverse_document_frequencies(document_texts: list[str]) -> dict[str, float]:
    """Map each term to log(total_documents / documents_containing_term) + 1."""
    total_document_count = max(len(document_texts), 1)
    documents_containing_term: dict[str, int] = {}
    for text in document_texts:
        for distinct_term in set(tokenize_into_terms(text)):
            documents_containing_term[distinct_term] = (
                documents_containing_term.get(distinct_term, 0) + 1
            )
    inverse_document_frequencies: dict[str, float] = {}
    for term, containing_count in documents_containing_term.items():
        inverse_document_frequencies[term] = (
            math.log(total_document_count / containing_count) + 1.0
        )
    return inverse_document_frequencies


def embed_text_as_tfidf_vector(
    text: str, inverse_document_frequencies: dict[str, float]
) -> dict[str, float]:
    """Represent text as a term -> (term_frequency * inverse_document_frequency) map.

    PRODUCTION SEAM: replace this body with a call to Vertex AI text embeddings
    and the ranking below matches by meaning instead of by exact word.
    """
    terms = tokenize_into_terms(text)
    if not terms:
        return {}
    term_frequencies: dict[str, int] = {}
    for term in terms:
        term_frequencies[term] = term_frequencies.get(term, 0) + 1
    term_count = len(terms)
    tfidf_vector: dict[str, float] = {}
    for term, frequency in term_frequencies.items():
        normalized_term_frequency = frequency / term_count
        weight = inverse_document_frequencies.get(term, 1.0)
        tfidf_vector[term] = normalized_term_frequency * weight
    return tfidf_vector


def cosine_similarity(
    first_vector: dict[str, float], second_vector: dict[str, float]
) -> float:
    """Cosine of the angle between two sparse term vectors; 0 when either is empty."""
    dot_product = sum(
        weight * second_vector[term]
        for term, weight in first_vector.items()
        if term in second_vector
    )
    first_magnitude = math.sqrt(sum(weight * weight for weight in first_vector.values()))
    second_magnitude = math.sqrt(sum(weight * weight for weight in second_vector.values()))
    if first_magnitude == 0.0 or second_magnitude == 0.0:
        return 0.0
    return dot_product / (first_magnitude * second_magnitude)


def rank_indexed_documents_by_relevance(
    question: str,
    indexed_documents: list[IndexedDocument],
    inverse_document_frequencies: dict[str, float],
) -> list[RankedDocument]:
    """Score every indexed document against the question, most relevant first."""
    question_vector = embed_text_as_tfidf_vector(question, inverse_document_frequencies)
    ranked_documents = [
        RankedDocument(
            document_id=document.document_id,
            category=document.category,
            text=document.text,
            similarity_score=cosine_similarity(question_vector, document.tfidf_vector),
        )
        for document in indexed_documents
    ]
    ranked_documents.sort(key=lambda ranked: ranked.similarity_score, reverse=True)
    return ranked_documents
