"""Load document corpora from disk and index them for retrieval (I/O edge).

Single responsibility: read the JSON corpus for a domain and turn it into an
in-memory, pre-vectorised index the pure retrieval core can score against.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from flash_dental_copilot.retrieval import (
    IndexedDocument,
    compute_inverse_document_frequencies,
    embed_text_as_tfidf_vector,
)

DATA_DIRECTORY = Path(__file__).resolve().parent / "data"

DOMAIN_DOCUMENT_FILENAMES = {
    "assets": "asset_service_documents.json",
    "technicians": "technician_performance_documents.json",
}


@dataclass(frozen=True)
class DomainCorpus:
    """Everything the API needs to answer questions for one domain."""
    domain_name: str
    indexed_documents: list[IndexedDocument]
    inverse_document_frequencies: dict[str, float]
    preset_questions: list[str]


def available_domain_names() -> list[str]:
    """The domains the copilot can answer over, e.g. 'assets' and 'technicians'."""
    return list(DOMAIN_DOCUMENT_FILENAMES)


def load_domain_corpus(domain_name: str) -> DomainCorpus:
    """Read one domain's documents from disk and index them for retrieval."""
    if domain_name not in DOMAIN_DOCUMENT_FILENAMES:
        raise KeyError(f"Unknown domain: {domain_name!r}")
    document_file = DATA_DIRECTORY / DOMAIN_DOCUMENT_FILENAMES[domain_name]
    corpus_payload = json.loads(document_file.read_text(encoding="utf-8"))
    raw_documents = corpus_payload["documents"]
    document_texts = [document["text"] for document in raw_documents]
    inverse_document_frequencies = compute_inverse_document_frequencies(document_texts)
    indexed_documents = [
        IndexedDocument(
            document_id=document["document_id"],
            category=document["category"],
            text=document["text"],
            tfidf_vector=embed_text_as_tfidf_vector(
                document["text"], inverse_document_frequencies
            ),
        )
        for document in raw_documents
    ]
    return DomainCorpus(
        domain_name=domain_name,
        indexed_documents=indexed_documents,
        inverse_document_frequencies=inverse_document_frequencies,
        preset_questions=corpus_payload.get("preset_questions", []),
    )
