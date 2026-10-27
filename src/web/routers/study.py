"""
Study Mode Router (Ticket 3.1) — /api/v2/study.
Provides endpoints for Flashcards, Multiple-Choice Quizzes, and Spaced Repetition Progress.
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from src.web.services.study_service import StudyService

router = APIRouter(prefix="/api/v2/study", tags=["study"])
study_service = StudyService()


class StudyProgressRequest(BaseModel):
    flashcard_id: str = Field(..., description="ID của thẻ ghi nhớ")
    rating: str = Field(..., description="Đánh giá ôn tập: easy | review | hard")


@router.get("/flashcards/{doc_id}")
async def get_document_flashcards(doc_id: str, limit: int = Query(10, ge=1, le=50)):
    """Lấy danh sách thẻ ghi nhớ flashcards tự động trích xuất từ tài liệu."""
    cards = study_service.generate_flashcards(doc_id=doc_id, max_cards=limit)
    return {
        "document_id": doc_id,
        "count": len(cards),
        "flashcards": cards
    }


@router.get("/quiz/{doc_id}")
async def get_document_quiz(doc_id: str, num_questions: int = Query(5, ge=1, le=20)):
    """Tạo bộ câu hỏi trắc nghiệm 4 lựa chọn (1 đúng + 3 phân tâm) từ tài liệu."""
    quiz_items = study_service.generate_quiz(doc_id=doc_id, num_questions=num_questions)
    return {
        "document_id": doc_id,
        "num_questions": len(quiz_items),
        "questions": quiz_items
    }


@router.post("/progress")
async def record_study_progress(req: StudyProgressRequest):
    """Ghi nhận tiến trình ôn tập ngắt quãng (Spaced Repetition) vào SQLite."""
    if req.rating not in ("easy", "review", "hard"):
        raise HTTPException(status_code=400, detail="rating phải thuộc ('easy', 'review', 'hard')")
    res = study_service.track_progress(flashcard_id=req.flashcard_id, rating=req.rating)
    return res
