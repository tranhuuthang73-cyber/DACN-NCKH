"""
Document Comparison Router (Ticket 3.2) — /api/v2/compare.
Provides endpoints for Pairwise Document Diffing and Cross-Document Question Answering.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from src.web.services.compare_service import CompareService

router = APIRouter(prefix="/api/v2/compare", tags=["compare"])
compare_service = CompareService()


class DocumentCompareRequest(BaseModel):
    doc_id_a: str = Field(..., description="ID của tài liệu thứ nhất (Document A)")
    doc_id_b: str = Field(..., description="ID của tài liệu thứ hai (Document B)")
    similarity_threshold: Optional[float] = Field(0.25, ge=0.0, le=1.0, description="Ngưỡng tương đồng token")


class CrossQARequest(BaseModel):
    query: str = Field(..., description="Câu hỏi đối chiếu giữa 2 tài liệu")
    doc_id_a: str = Field(..., description="ID của tài liệu A")
    doc_id_b: str = Field(..., description="ID của tài liệu B")
    top_k: Optional[int] = Field(4, ge=1, le=10, description="Số đoạn trích xuất mỗi tài liệu")


@router.post("")
async def compare_documents_endpoint(req: DocumentCompareRequest):
    """Thực hiện đối soát song song và bóc tách điểm giống/khác giữa 2 tài liệu."""
    try:
        res = compare_service.compare_documents(
            doc_id_a=req.doc_id_a,
            doc_id_b=req.doc_id_b,
            similarity_threshold=req.similarity_threshold or 0.25
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi so sánh tài liệu: {str(e)}")


@router.post("/qa")
async def cross_document_qa_endpoint(req: CrossQARequest):
    """Hỏi đáp đối chứng tổng hợp thông tin từ 2 tài liệu khác nhau."""
    try:
        res = compare_service.cross_qa(
            query=req.query,
            doc_id_a=req.doc_id_a,
            doc_id_b=req.doc_id_b,
            top_k=req.top_k or 4
        )
        return res
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi hỏi đáp chéo: {str(e)}")
