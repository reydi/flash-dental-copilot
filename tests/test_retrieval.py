"""Tests for the pure retrieval core: tokenizing, IDF, embedding, cosine, ranking."""
from __future__ import annotations

import pytest

from flash_dental_copilot.retrieval import (
    IndexedDocument,
    compute_inverse_document_frequencies,
    cosine_similarity,
    embed_text_as_tfidf_vector,
    rank_indexed_documents_by_relevance,
    tokenize_into_terms,
)


def test_tokenize_drops_stop_words_and_single_characters():
    terms = tokenize_into_terms("The suction motor on FD-1042 is a problem")
    assert "suction" in terms
    assert "motor" in terms
    assert "the" not in terms  # stop-word
    assert "is" not in terms  # stop-word
    assert "a" not in terms  # single character


def test_rare_term_has_higher_inverse_document_frequency_than_common_term():
    document_texts = [
        "suction motor replaced",
        "suction motor replaced again",
        "hydraulic seal replaced",
    ]
    inverse_document_frequencies = compute_inverse_document_frequencies(document_texts)
    # Look terms up by their stemmed form, since tokenizing stems everything.
    (rare_term,) = tokenize_into_terms("hydraulic")
    (common_term,) = tokenize_into_terms("replaced")
    # "hydraulic" appears in one doc, "replaced" in all three -> hydraulic weighs more.
    assert inverse_document_frequencies[rare_term] > inverse_document_frequencies[common_term]


def test_empty_text_embeds_to_empty_vector():
    assert embed_text_as_tfidf_vector("", {"suction": 2.0}) == {}


def test_cosine_similarity_is_one_for_identical_vectors_and_zero_for_disjoint():
    first_vector = {"suction": 1.0, "motor": 1.0}
    assert cosine_similarity(first_vector, first_vector) == pytest.approx(1.0)
    assert cosine_similarity(first_vector, {"hydraulic": 1.0}) == 0.0


def test_ranking_puts_the_matching_document_first():
    inverse_document_frequencies = compute_inverse_document_frequencies(
        ["suction motor failure", "hydraulic leak sealed"]
    )
    indexed_documents = [
        IndexedDocument(
            document_id="hydraulic",
            category="service_log",
            text="hydraulic leak sealed",
            tfidf_vector=embed_text_as_tfidf_vector(
                "hydraulic leak sealed", inverse_document_frequencies
            ),
        ),
        IndexedDocument(
            document_id="suction",
            category="service_log",
            text="suction motor failure",
            tfidf_vector=embed_text_as_tfidf_vector(
                "suction motor failure", inverse_document_frequencies
            ),
        ),
    ]
    ranked = rank_indexed_documents_by_relevance(
        "why did the suction motor fail", indexed_documents, inverse_document_frequencies
    )
    assert ranked[0].document_id == "suction"
    assert ranked[0].similarity_score > ranked[1].similarity_score
