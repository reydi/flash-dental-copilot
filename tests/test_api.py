"""End-to-end tests for the HTTP API, exercised through FastAPI's TestClient."""
from __future__ import annotations

from fastapi.testclient import TestClient

from flash_dental_copilot.api import application

client = TestClient(application)


def test_health_endpoint_reports_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_asset_story_question_returns_a_grounded_cited_answer():
    response = client.post(
        "/ask",
        json={"domain": "assets", "question": "asset FD-1042 keeps failing — show its service history"},
    )
    body = response.json()
    assert response.status_code == 200
    assert body["abstained"] is False
    assert "FD-1042" in body["citation_document_id"]
    assert body["similarity_score"] > 0.12
    assert "warranty" in body["kpi_summary"]


def test_out_of_scope_question_abstains():
    response = client.post(
        "/ask", json={"domain": "assets", "question": "what is the wifi password"}
    )
    body = response.json()
    assert body["abstained"] is True
    assert body["citation_document_id"] is None
    assert "Not in our records" in body["answer_text"]


def test_technician_question_retrieves_the_technician_record():
    response = client.post(
        "/ask",
        json={"domain": "technicians", "question": "how many jobs did Yudi close and his first-time-fix"},
    )
    body = response.json()
    assert body["abstained"] is False
    assert "Yudi" in body["answer_text"]
    assert "first-time-fix" in body["kpi_summary"]


def test_answer_always_carries_a_pii_masked_example():
    response = client.post(
        "/ask", json={"domain": "assets", "question": "suction motor"}
    )
    body = response.json()
    assert "[PERSON_1]" in body["pii_masking_example"]
    assert "Yudi Pratama" not in body["pii_masking_example"]


def test_unknown_domain_returns_404():
    response = client.post("/ask", json={"domain": "spaceships", "question": "hello"})
    assert response.status_code == 404
