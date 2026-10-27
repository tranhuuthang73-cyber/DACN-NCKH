"""
Export Service — Session & Knowledge Export Engine (Ticket 3.3).
Exports chat transcripts and research telemetry to Markdown, JSON, and PDF,
and flashcards to Anki-compatible CSV.
100% offline, zero remote dependencies, frozen inference only.
"""

import io
import csv
import json
import time
from typing import Dict, Any, List, Optional
from src.web.database.connection import get_db_connection
from src.web.services.pipeline_service import PipelineService
from src.web.services.study_service import StudyService


class ExportService:
    """Service to export chat sessions, telemetry, and study flashcards."""

    def __init__(
        self,
        pipeline_service: Optional[PipelineService] = None,
        study_service: Optional[StudyService] = None,
    ):
        self.pipeline_service = pipeline_service or PipelineService.get_instance()
        self.study_service = study_service or StudyService(self.pipeline_service)

    def get_session_data(self, session_id: str) -> Dict[str, Any]:
        """Fetch session metadata and chronological messages from SQLite or session manager."""
        session_meta = None
        messages = []

        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM chat_sessions WHERE id = ?", (session_id,))
            row = cursor.fetchone()
            if row:
                session_meta = dict(row)

            cursor.execute(
                "SELECT * FROM messages WHERE session_id = ? ORDER BY created_at ASC",
                (session_id,),
            )
            for r in cursor.fetchall():
                messages.append(dict(r))

        if not session_meta:
            # Fallback to SessionManager in memory
            sm_session = self.pipeline_service.session_manager.get_session(session_id)
            if sm_session:
                session_meta = {
                    "id": sm_session.session_id,
                    "title": sm_session.title,
                    "created_at": sm_session.created_at,
                    "updated_at": sm_session.updated_at,
                }
                messages = [m.to_dict() for m in sm_session.messages]
            else:
                session_meta = {
                    "id": session_id,
                    "title": f"Phiên hỏi đáp #{session_id[:8]}",
                    "created_at": time.time(),
                    "updated_at": time.time(),
                }

        return {
            "session": session_meta,
            "messages": messages,
            "message_count": len(messages),
        }

    def export_session_markdown(self, session_id: str) -> str:
        """Export session conversation transcript to GitHub Flavored Markdown."""
        data = self.get_session_data(session_id)
        session = data["session"]
        messages = data["messages"]

        created_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(session.get("created_at") or time.time()))

        lines = [
            f"# 🧠 NeuroRead Studio — Biên Bản Phiên Hỏi Đáp",
            f"",
            f"**Tiêu đề:** {session.get('title', 'Phiên làm việc')}",
            f"",
            f"| Thông số | Giá trị |",
            f"| :--- | :--- |",
            f"| **Session ID** | `{session_id}` |",
            f"| **Thời gian tạo** | {created_str} |",
            f"| **Số lượng lượt trao đổi** | {len(messages)} |",
            f"| **Mô hình nền** | SmolLM2-135M (Đóng băng 100%) |",
            f"| **Bộ nhớ tham số** | SA-CMS Continuum Memory 5.31M |",
            f"| **Môi trường** | 100% Ngoại tuyến (Zero Cloud Egress) |",
            f"",
            f"---",
            f"",
            f"## 📝 Nhật Ký Hội Thoại & Đối Soát Căn Cứ",
            f"",
        ]

        if not messages:
            lines.append("*(Chưa có tin nhắn nào trong phiên này)*\n")

        for idx, m in enumerate(messages, start=1):
            role = m.get("role", "unknown")
            content = m.get("content", "")
            time_str = ""
            if m.get("created_at"):
                time_str = f" *({time.strftime('%H:%M:%S', time.localtime(m['created_at']))})*"

            if role == "user":
                lines.append(f"### 👤 Lượt {idx} — Người dùng{time_str}")
                lines.append(f"{content}\n")
            elif role == "assistant":
                lines.append(f"### 🧠 Lượt {idx} — Trợ lý SA-CMS{time_str}")
                lines.append(f"{content}\n")

                citations = m.get("citations")
                if citations:
                    if isinstance(citations, str):
                        try:
                            citations = json.loads(citations)
                        except Exception:
                            citations = [citations]
                    if citations:
                        cit_str = ", ".join(f"`{c}`" for c in citations)
                        lines.append(f"> 📄 **Căn cứ trích dẫn:** {cit_str}\n")

                in_tok = m.get("input_tokens", 0)
                out_tok = m.get("output_tokens", 0)
                lat = m.get("latency_ms", 0.0)
                mode = m.get("mode", "hybrid")
                lines.append(
                    f"*(Telemetry: Input: {in_tok} tok · Output: {out_tok} tok · Độ trễ: {lat:.1f} ms · Chế độ: {mode})*\n"
                )
            else:
                lines.append(f"### ⚙️ {role.capitalize()}{time_str}")
                lines.append(f"{content}\n")

        lines.append("\n---\n*Biên bản được xuất tự động từ hệ thống NeuroRead Desktop & Web Studio.*")
        return "\n".join(lines)

    def export_session_json(self, session_id: str) -> Dict[str, Any]:
        """Export session transcript and telemetry in structured JSON format."""
        data = self.get_session_data(session_id)
        data["exported_at"] = time.time()
        data["system"] = {
            "app": "NeuroRead Studio",
            "version": "5.2.0",
            "model": "SmolLM2-135M",
            "memory_parameters": "5.31M",
            "offline_mode": True,
        }
        return data

    def export_session_pdf(self, session_id: str) -> bytes:
        """Export session transcript to a printable PDF document using ReportLab."""
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

        data = self.get_session_data(session_id)
        session = data["session"]
        messages = data["messages"]

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "DocTitle",
            parent=styles["Heading1"],
            fontSize=18,
            leading=22,
            textColor=colors.HexColor("#1e293b"),
            spaceAfter=12,
        )
        h2_style = ParagraphStyle(
            "SectionH2",
            parent=styles["Heading2"],
            fontSize=13,
            leading=16,
            textColor=colors.HexColor("#334155"),
            spaceBefore=10,
            spaceAfter=6,
        )
        body_style = ParagraphStyle(
            "Body",
            parent=styles["Normal"],
            fontSize=9.5,
            leading=13,
            textColor=colors.HexColor("#1e293b"),
        )
        meta_style = ParagraphStyle(
            "Meta",
            parent=styles["Normal"],
            fontSize=8,
            leading=10,
            textColor=colors.HexColor("#64748b"),
        )

        story = []

        # Title
        story.append(Paragraph(f"NeuroRead Studio — Biên Bản Phiên #{session_id[:8]}", title_style))
        story.append(Paragraph(f"<b>Tiêu đề:</b> {session.get('title', 'Phiên hội thoại')}", h2_style))
        story.append(Spacer(1, 8))

        # Metadata Table
        created_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(session.get("created_at") or time.time()))
        table_data = [
            ["Session ID", session_id],
            ["Thời gian", created_str],
            ["Mô hình", "SmolLM2-135M (Frozen) + 5.31M SA-CMS"],
            ["Trạng thái", "100% Offline Local Inference"],
        ]
        t = Table(table_data, colWidths=[110, 420])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
            ("TEXTCOLOR", (0, 0), (-1, -1), colors.HexColor("#1e293b")),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("FONTSIZE", (0, 0), (-1, -1), 8.5),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(t)
        story.append(Spacer(1, 14))

        # Messages Stream
        story.append(Paragraph("Nhật Ký Hội Thoại:", h2_style))
        for idx, m in enumerate(messages, start=1):
            role = m.get("role", "unknown")
            content = m.get("content", "").replace("\n", "<br/>")

            if role == "user":
                story.append(Paragraph(f"<b>Người dùng [{idx}]:</b> {content}", body_style))
            else:
                story.append(Paragraph(f"<b>Trợ lý SA-CMS [{idx}]:</b> {content}", body_style))
                citations = m.get("citations")
                if citations:
                    if isinstance(citations, str):
                        try:
                            citations = json.loads(citations)
                        except Exception:
                            citations = [citations]
                    if citations:
                        cit_str = ", ".join(citations)
                        story.append(Paragraph(f"<i>Căn cứ: {cit_str}</i>", meta_style))

            story.append(Spacer(1, 6))

        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

    def export_flashcards_csv(self, doc_id: str) -> str:
        """Export flashcards in Anki/Quizlet compatible CSV format."""
        flashcards = self.study_service.generate_flashcards(doc_id=doc_id, max_cards=50)

        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        # Header for Anki / CSV import
        writer.writerow(["Question", "Answer", "Level", "Citation", "Status"])

        for fc in flashcards:
            writer.writerow([
                fc.get("question", ""),
                fc.get("answer", ""),
                fc.get("level", "Mức 1"),
                fc.get("source_passage_id", ""),
                fc.get("status", "new"),
            ])

        return output.getvalue()
