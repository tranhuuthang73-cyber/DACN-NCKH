"""
Tests for Export Service & REST API (Ticket 3.3).
Verifies Markdown, JSON, PDF export for sessions and CSV export for flashcards.
"""

import pytest
from fastapi.testclient import TestClient

from src.web.app import app
from src.web.services.export_service import ExportService


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_export_session_markdown():
    """Verify Markdown export contains proper title, table, and formatting."""
    service = ExportService()
    md_content = service.export_session_markdown("TEST_SESSION_EXPORT_001")

    assert "# 🧠 NeuroRead Studio" in md_content
    assert "SmolLM2-135M" in md_content
    assert "100% Ngoại tuyến" in md_content


def test_export_session_json():
    """Verify JSON export contains structured session dictionary and system metadata."""
    service = ExportService()
    data = service.export_session_json("TEST_SESSION_EXPORT_001")

    assert "session" in data
    assert "messages" in data
    assert "system" in data
    assert data["system"]["model"] == "SmolLM2-135M"
    assert data["system"]["offline_mode"] is True


def test_export_session_pdf():
    """Verify PDF export generates valid PDF binary bytes with %PDF magic header."""
    service = ExportService()
    pdf_bytes = service.export_session_pdf("TEST_SESSION_EXPORT_001")

    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 500
    assert pdf_bytes.startswith(b"%PDF")


def test_export_flashcards_csv():
    """Verify flashcard export generates standard CSV with Question, Answer, and Citation columns."""
    service = ExportService()
    csv_str = service.export_flashcards_csv("DEMO_DOC_001")

    assert "Question,Answer,Level,Citation,Status" in csv_str
    lines = csv_str.strip().split("\n")
    assert len(lines) >= 2


def test_export_api_endpoints(client):
    """Verify /api/v2/export endpoints return appropriate media types."""
    # 1. GET /api/v2/export/session/{id}?format=md
    res_md = client.get("/api/v2/export/session/TEST_SESS_001?format=md")
    assert res_md.status_code == 200
    assert "text/markdown" in res_md.headers["content-type"]
    assert "NeuroRead" in res_md.text

    # 2. GET /api/v2/export/session/{id}?format=json
    res_json = client.get("/api/v2/export/session/TEST_SESS_001?format=json")
    assert res_json.status_code == 200
    assert res_json.json()["system"]["offline_mode"] is True

    # 3. GET /api/v2/export/session/{id}?format=pdf
    res_pdf = client.get("/api/v2/export/session/TEST_SESS_001?format=pdf")
    assert res_pdf.status_code == 200
    assert res_pdf.headers["content-type"] == "application/pdf"
    assert res_pdf.content.startswith(b"%PDF")

    # 4. GET /api/v2/export/flashcards/{doc_id}?format=csv
    res_csv = client.get("/api/v2/export/flashcards/DEMO_DOC_001?format=csv")
    assert res_csv.status_code == 200
    assert "text/csv" in res_csv.headers["content-type"]
    assert "Question,Answer" in res_csv.text
