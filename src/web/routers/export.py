"""
Export Router (Ticket 3.3) — /api/v2/export.
Provides endpoints to export chat sessions (Markdown, JSON, PDF)
and study flashcards (CSV for Anki, JSON).
"""

from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import PlainTextResponse

from src.web.services.export_service import ExportService

router = APIRouter(prefix="/api/v2/export", tags=["export"])
export_service = ExportService()


@router.get("/session/{session_id}")
async def export_session_endpoint(
    session_id: str,
    format: str = Query("json", pattern="^(md|markdown|json|pdf)$", description="Định dạng xuất: md | json | pdf")
):
    """Xuất biên bản phiên hội thoại ra Markdown, JSON hoặc PDF."""
    fmt = format.lower()

    if fmt in ("md", "markdown"):
        content = export_service.export_session_markdown(session_id)
        return PlainTextResponse(
            content,
            media_type="text/markdown",
            headers={"Content-Disposition": f'attachment; filename="neuroread_session_{session_id[:8]}.md"'}
        )

    elif fmt == "pdf":
        try:
            pdf_bytes = export_service.export_session_pdf(session_id)
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={"Content-Disposition": f'attachment; filename="neuroread_session_{session_id[:8]}.pdf"'}
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Lỗi khi xuất file PDF: {str(e)}")

    else:
        # Default JSON
        return export_service.export_session_json(session_id)


@router.get("/flashcards/{doc_id}")
async def export_flashcards_endpoint(
    doc_id: str,
    format: str = Query("csv", pattern="^(csv|json)$", description="Định dạng xuất: csv | json")
):
    """Xuất bộ thẻ ghi nhớ của tài liệu ra file CSV nhập vào Anki hoặc JSON."""
    fmt = format.lower()

    if fmt == "csv":
        csv_content = export_service.export_flashcards_csv(doc_id)
        return PlainTextResponse(
            csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": f'attachment; filename="flashcards_{doc_id}.csv"'}
        )
    else:
        cards = export_service.study_service.generate_flashcards(doc_id)
        return {
            "document_id": doc_id,
            "count": len(cards),
            "flashcards": cards
        }
