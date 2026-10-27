"""
Tests for Study Mode Service & API (Ticket 3.1).
Verifies flashcard generation, quiz generation, progress tracking, and REST endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from src.web.app import app
from src.web.services.study_service import StudyService


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_study_service_generate_flashcards():
    """Verify flashcards generation returns valid list of Q&A cards."""
    service = StudyService()
    cards = service.generate_flashcards("DEMO_DOC_001", max_cards=5)

    assert isinstance(cards, list)
    assert len(cards) > 0
    first = cards[0]
    assert "question" in first and len(first["question"]) > 5
    assert "answer" in first and len(first["answer"]) > 5
    assert "source_passage_id" in first
    assert first["status"] == "new"


def test_study_service_generate_quiz():
    """Verify quiz generation returns 4-option multiple-choice items with 1 correct answer."""
    service = StudyService()
    quiz_items = service.generate_quiz("DEMO_DOC_001", num_questions=3)

    assert isinstance(quiz_items, list)
    assert len(quiz_items) == 3

    for item in quiz_items:
        assert "question" in item
        assert "options" in item
        assert len(item["options"]) == 4
        assert 0 <= item["correct_index"] <= 3
        assert "explanation" in item
        assert "citation" in item


def test_study_service_track_progress():
    """Verify spaced repetition progress tracking updates SQLite flashcard record."""
    service = StudyService()
    cards = service.generate_flashcards("DEMO_DOC_001", max_cards=2)
    card_id = cards[0]["id"]

    res = service.track_progress(flashcard_id=card_id, rating="easy")
    assert res["flashcard_id"] == card_id
    assert res["status"] == "mastered"
    assert res["recorded"] is True
    assert res["next_review_at"] > 0


def test_study_api_endpoints(client):
    """Verify /api/v2/study endpoints return HTTP 200 with proper payloads."""
    # 1. GET /api/v2/study/flashcards/{doc_id}
    res_fc = client.get("/api/v2/study/flashcards/DEMO_DOC_001?limit=4")
    assert res_fc.status_code == 200
    data_fc = res_fc.json()
    assert data_fc["document_id"] == "DEMO_DOC_001"
    assert len(data_fc["flashcards"]) > 0

    # 2. GET /api/v2/study/quiz/{doc_id}
    res_quiz = client.get("/api/v2/study/quiz/DEMO_DOC_001?num_questions=3")
    assert res_quiz.status_code == 200
    data_quiz = res_quiz.json()
    assert len(data_quiz["questions"]) == 3

    # 3. POST /api/v2/study/progress
    card_id = data_fc["flashcards"][0]["id"]
    res_prog = client.post("/api/v2/study/progress", json={"flashcard_id": card_id, "rating": "review"})
    assert res_prog.status_code == 200
    data_prog = res_prog.json()
    assert data_prog["status"] == "review"
