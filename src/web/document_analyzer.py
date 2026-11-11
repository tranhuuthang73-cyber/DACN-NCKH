"""
Phase 5.9 Extension — Document Intelligence & Auto Question Generator.
Extracts structured executive summaries, key takeaways, and generates
diverse, relevant, document-grounded questions from hierarchical SA-CMS structures.
100% Local Offline, Zero External API, Zero Network Egress.
"""

import re
import unicodedata
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path


def strip_accents(s: str) -> str:
    """Removes Vietnamese tone marks for accent-insensitive matching."""
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return s.replace("đ", "d").replace("Đ", "D")


class DocumentAnalyzer:
    """
    Analyzes document structures to synthesize key points and generate
    insightful, grounded questions tailored to the document's content.
    """

    STOPWORDS_VI = {
        "và", "của", "các", "những", "trong", "để", "với", "cho", "tại", "là",
        "có", "được", "khi", "này", "đó", "theo", "về", "như", "một", "nhiều",
        "thì", "mà", "từ", "ở", "ra", "đã", "sẽ", "đang", "bởi", "do", "bằng",
    }

    @staticmethod
    def _clean_text(text: str) -> str:
        """Removes citation markers and excess whitespace."""
        clean = re.sub(r"\[?[A-Z0-9_\-]+::P\d+\]?", "", text)
        clean = re.sub(r"_[A-Z0-9_]+::P\d+\]?", "", clean)
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean

    @classmethod
    def _split_clean_sentences(cls, text: str) -> List[str]:
        """Splits text into meaningful sentences."""
        clean = cls._clean_text(text)
        raw_sents = re.split(r"(?<=[.!?])\s+|\n+", clean)
        sentences = []
        for s in raw_sents:
            s_stripped = s.strip()
            # Ignore numbered headers like "1. ", "1.1 "
            s_stripped = re.sub(r"^\d+(\.\d+)*\.?\s*", "", s_stripped)
            if len(s_stripped) >= 20 and not s_stripped.startswith("#"):
                sentences.append(s_stripped)
        return sentences

    @classmethod
    def extract_key_points_and_summary(
        cls,
        raw_text: str,
        title: str = "Tài liệu",
        max_points: int = 4,
    ) -> Dict[str, Any]:
        """
        Extracts high-level executive summary and 3-4 key takeaways.
        """
        all_sentences = cls._split_clean_sentences(raw_text)
        if not all_sentences:
            return {
                "overview": f"Tài liệu {title} đã được nạp thành công vào hệ thống bộ nhớ tham số SA-CMS.",
                "key_points": [f"Nội dung tài liệu '{title}' bao gồm các phần kiến trúc và dữ kiện kỹ thuật liên quan."],
            }

        key_points = []
        try:
            from src.brain.textrank_salience import select_key_points
            key_points = select_key_points(all_sentences, k=max_points)
        except Exception:
            key_points = []

        if not key_points:
            # Fallback to legacy heuristic scoring + distinct prefix selection
            scored_sentences = []
            for s in all_sentences:
                score = 0.0
                s_lower = s.lower()
                # Informational keywords
                if any(k in s_lower for k in ["mục tiêu", "nghiên cứu", "đề xuất", "hệ thống", "kiến trúc", "mô hình"]):
                    score += 3.0
                if any(k in s_lower for k in ["kết quả", "hiệu năng", "đạt", "đánh giá", "tối ưu"]):
                    score += 2.5
                if any(k in s_lower for k in ["hạn chế", "thách thức", "vấn đề", "khó khăn"]):
                    score += 2.0
                if re.search(r"\d+(\.\d+)?\s*(%|token|ms|gb|mb|triệu|nghìn)", s_lower):
                    score += 2.0
                # Length sanity check (prefer 40 - 200 chars)
                if 40 <= len(s) <= 220:
                    score += 1.0

                scored_sentences.append((score, s))

            scored_sentences.sort(key=lambda x: x[0], reverse=True)

            # Pick top distinct points
            seen = set()
            for _, s in scored_sentences:
                first_few = " ".join(s.split()[:4]).lower()
                if first_few not in seen:
                    seen.add(first_few)
                    key_points.append(s)
                if len(key_points) >= max_points:
                    break

            if not key_points:
                key_points = all_sentences[:max_points]

        lead = key_points[0] if key_points else "Tài liệu kỹ thuật chuyên ngành."
        overview = f"Tài liệu '{title}' tập trung vào các nội dung trọng tâm: {lead}"

        return {
            "overview": overview,
            "key_points": key_points,
        }

    @classmethod
    def build_document_knowledge_blueprint(
        cls,
        raw_text: str,
        title: str = "Tài liệu",
    ) -> str:
        """
        Synthesizes a comprehensive VIP Multi-Tier Document Knowledge Blueprint:
        - L1 TL;DR & L2 Executive Synthesis (via ProgressiveSummarizer)
        - Key structural points & headings
        - Extracted quantitative metrics & benchmarks (% / MB / GB / ms / parameters)
        Uses zero raw '###' or single-asterisk '*italic*' so frontend renders cleanly.
        """
        summary_data = cls.extract_key_points_and_summary(raw_text, title=title, max_points=6)
        overview = summary_data.get("overview", "")
        key_points = summary_data.get("key_points", [])

        l1_tldr = overview
        l2_exec = ""
        try:
            from src.brain.progressive_summarizer import ProgressiveSummarizer
            ps = ProgressiveSummarizer().generate_digest(raw_text, doc_title=title)
            if ps.l1_tldr:
                l1_tldr = ps.l1_tldr
            if ps.l2_executive:
                l2_exec = ps.l2_executive
        except Exception:
            pass

        # Extract section headings if present
        headings = []
        for line in raw_text.splitlines():
            l_str = line.strip()
            if l_str.startswith("#"):
                h_clean = l_str.lstrip("#").strip()
                if h_clean and h_clean not in headings:
                    headings.append(h_clean)

        # Extract quantitative metrics
        metrics_found = []
        for m in re.finditer(
            r"\b(\d+(?:[.,]\d+)?\s*(?:%|(?:MB|GB|KB|ms|s|tokens?|triệu(?:\s+tham\s+số)?|tỷ|tầng|lớp)\b))",
            raw_text,
            re.IGNORECASE,
        ):
            val_str = m.group(1).strip()
            if val_str not in metrics_found:
                metrics_found.append(val_str)

        blocks = [
            f"📖 **BẢN ĐỒ TRI THỨC TÀI LIỆU: {title}**",
            f"🎯 **Tóm lược cốt lõi (TL;DR):** {l1_tldr}",
        ]
        if l2_exec and l2_exec.strip() != l1_tldr.strip():
            blocks.append(f"🧭 **Tổng hợp điều hành:**\n{l2_exec}")

        if headings:
            h_badges = " • ".join(f"`{h}`" for h in headings[:6])
            blocks.append(f"🗂️ **Cấu trúc chương mục:** {h_badges}")

        if key_points:
            pts_str = "\n".join(f"- {pt}" for pt in key_points[:6])
            blocks.append(f"📌 **Các luận điểm & phát hiện trọng tâm:**\n{pts_str}")

        if metrics_found:
            m_badges = ", ".join(f"**{m}**" for m in metrics_found[:8])
            blocks.append(f"📊 **Chỉ số & thông số định lượng nổi bật:** {m_badges}")

        return "\n\n".join(blocks)

    @classmethod
    def generate_suggested_questions(
        cls,
        raw_text: str,
        title: str = "Tài liệu",
        max_questions: int = 6,
    ) -> List[Dict[str, Any]]:
        """
        Automatically generates diverse, relevant, document-grounded questions.
        Covers definitions, mechanisms, limitations, quantitative facts, and overviews.
        """
        questions = []
        seen_queries = set()

        def add_q(q_text: str, category: str, sample_ans: str = ""):
            clean_q = q_text.strip()
            if clean_q and clean_q.lower() not in seen_queries:
                seen_queries.add(clean_q.lower())
                questions.append({
                    "question": clean_q,
                    "category": category,
                    "sample_answer_excerpt": sample_ans[:160] if sample_ans else "",
                })

        # Pattern 0: Specific Topics / Modules (e.g. "Topic 1: ...", "Topic 11: ...", "Chủ đề 2:")
        topic_pattern = re.compile(
            r"^\s*(Topic|Chủ đề|Bài|Mục|Section)\s*(\d+)[:\-\.\s]+([^\n\.\?]{3,65})",
            re.IGNORECASE | re.MULTILINE,
        )
        for tm in topic_pattern.finditer(raw_text):
            pfx, num_str, t_name = tm.group(1).title(), tm.group(2), tm.group(3).strip()
            add_q(f"Yêu cầu và nội dung chính của {pfx} {num_str} ({t_name[:45]}) là gì?", "Chủ đề bài học", tm.group(0))
            if len(questions) >= 3:
                break

        # Pattern 1: Section-based Questions (Level 2 SA-CMS structure - highest fidelity)
        lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
        for line in lines:
            # Matches: "## 1. Quy hoạch Điện VIII", "### 2. Kiến trúc", "1. Đặt vấn đề"
            h_match = re.match(r"^(#{1,4}\s*)?(\d+(\.\d+)*\.?\s*)?([A-ZÀ-Ỹ][^\n:]{4,55})$", line)
            if h_match:
                sec_name = h_match.group(4).strip()
                # Skip generic headers
                if any(g in sec_name.lower() for g in ["tài liệu tham khảo", "mục lục", "references", "phụ lục", "overview"]):
                    continue
                q = f"Thông tin cốt lõi được trình bày tại mục '{sec_name}' là gì?"
                add_q(q, "Tra cứu Chương mục", sec_name)
            if len(questions) >= 3:
                break

        # Pattern 2: Concept & Definitions ("là gì", "được định nghĩa")
        def_pattern = re.compile(
            r"([A-ZÀ-Ỹa-zà-ỹ0-9_\-\s]{3,35})\s+(là\s+gì|là\s+một|được\s+(xác định|hiểu|định nghĩa)\s+là|đóng\s+vai\s+trò\s+là)\s+([^.!?]+)",
            re.IGNORECASE,
        )
        for m in def_pattern.finditer(raw_text):
            subject = m.group(1).strip()
            subject = re.sub(r"^(ở|tại|theo|trong|với|khi)\s+", "", subject, flags=re.IGNORECASE).strip()
            if 2 <= len(subject.split()) <= 6 and not subject.startswith("#"):
                q = f"{subject} là gì và có vai trò như thế nào?"
                add_q(q, "Định nghĩa & Khái niệm", m.group(0))
            if len(questions) >= 4:
                break

        # Pattern 3: Limitations / Problems ("Hạn chế", "Nhược điểm", "Thách thức")
        limit_pattern = re.compile(
            r"(hạn\s+chế|nhược\s+điểm|thách\s+thức|khó\s+khăn|vấn\s+đề)\s+(ở\s+đây|của\s+hệ\s+thống|chính|được\s+xác\s+định|trong)?\s*[:\s]+([^.!?]+)",
            re.IGNORECASE,
        )
        for m in limit_pattern.finditer(raw_text):
            excerpt = m.group(0).strip()
            add_q(f"Những hạn chế hoặc thách thức nào được chỉ rõ trong '{title}'?", "Hạn chế & Thách thức", excerpt)
            break

        # Pattern 4: Mechanism / Architecture / Solutions ("mô hình", "kiến trúc", "phương pháp", "giải pháp")
        mech_pattern = re.compile(
            r"(hệ\s+thống|mô\s+hình|kiến\s+trúc|phương\s+pháp|thuật\s+toán)\s+([A-ZÀ-Ỹa-zà-ỹ0-9_\-\s]{4,30})\s+(hoạt\s+động|kết\s+hợp|áp\s+dụng|đạt\s+được|bao\s+gồm)",
            re.IGNORECASE,
        )
        for m in mech_pattern.finditer(raw_text):
            name = m.group(2).strip()
            if 2 <= len(name.split()) <= 6:
                q = f"Kiến trúc hoặc cơ chế hoạt động của {name} như thế nào?"
                add_q(q, "Kiến trúc & Cơ chế", m.group(0))
            if len(questions) >= 5:
                break

        # Pattern 5: Quantitative Metrics / Numbers ("%", "ms", "MB", "GB", "tokens")
        num_pattern = re.compile(
            r"([^.!?\n]{15,90}\b\d+(\.\d+)?\s*(%|token|ms|gb|mb|mw|triệu|nghìn)\b[^.!?\n]{10,60})",
            re.IGNORECASE,
        )
        for m in num_pattern.finditer(raw_text):
            excerpt = m.group(1).strip()
            add_q(f"Tài liệu ghi nhận những kết quả hoặc số liệu định lượng cụ thể nào?", "Số liệu & Định lượng", excerpt)
            break

        # Fallback questions with guaranteed document relevance
        defaults = [
            (f"Tài liệu '{title}' tóm tắt những nội dung chính nào?", "Tổng quan"),
            (f"Các giải pháp kỹ thuật chính được đề xuất trong '{title}' là gì?", "Giải pháp"),
            (f"Mục tiêu trọng tâm của '{title}' được xác định như thế nào?", "Mục tiêu"),
        ]
        for def_q, def_cat in defaults:
            if len(questions) < max_questions:
                add_q(def_q, def_cat)

        return questions[:max_questions]

    @classmethod
    def find_best_grounded_answer(
        cls,
        query: str,
        evidence_passages: List[Any],
        answer_mode: str = "balanced",
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Locates the exact span answering the query from the evidence passages.

        Two invariants are enforced:
        1. Precision — the returned core is the minimal clause that answers the
           question (answering "bao nhiêu %" never returns the whole paragraph).
        2. Question tail — every answer ends with a self-study question block.
        """
        from src.hybrid_qa.answer_span import (
            ensure_trailing_question,
            extract_answer_span,
            generate_followup_questions,
            relevance_score,
            select_best_sentence,
            split_sentences,
            strip_question_block,
        )

        MIN_RELEVANCE = 0.34

        if not evidence_passages:
            return "Không tìm thấy đủ thông tin bằng chứng trong tài liệu để trả lời câu hỏi này.", []

        # Collect every sentence from every evidence passage.
        sentence_pool: List[str] = []
        sentence_sections: List[str] = []
        for passage in evidence_passages:
            passage_text = getattr(passage, "text", "") if hasattr(passage, "text") else str(passage)
            passage_section = getattr(passage, "section_title", "") or ""
            for sentence in split_sentences(passage_text):
                sentence_pool.append(sentence)
                sentence_sections.append(passage_section)

        from src.web.token_optimizer import expand_query_semantics
        exp_query, _ = expand_query_semantics(query)

        best_sentence = select_best_sentence(exp_query, sentence_pool, sentence_sections)
        best_passage_idx = 0
        if best_sentence:
            for idx, passage in enumerate(evidence_passages):
                passage_text = getattr(passage, "text", "") if hasattr(passage, "text") else str(passage)
                if best_sentence[:40] in cls._clean_text(passage_text):
                    best_passage_idx = idx
                    break
        elif sentence_pool:
            best_sentence = sentence_pool[0]

        # Relevance gate: refuse instead of answering from an unrelated passage.
        matched_section = ""
        if best_sentence in sentence_pool:
            matched_section = sentence_sections[sentence_pool.index(best_sentence)]
        combined_pool_text = " ".join(sentence_pool[:4])
        combined_sec_text = " ".join(sentence_sections[:4])
        rel = max(
            relevance_score(query, best_sentence, extra=matched_section),
            relevance_score(exp_query, best_sentence, extra=matched_section),
            relevance_score(query, combined_pool_text, extra=combined_sec_text) * 0.85,
            relevance_score(exp_query, combined_pool_text, extra=combined_sec_text) * 0.85,
        )
        if not best_sentence or rel < MIN_RELEVANCE:
            return "Không tìm thấy đủ thông tin bằng chứng trong tài liệu để trả lời câu hỏi này.", []

        # Deduplicate citations: one citation per distinct document & section.
        dedup_citations = []
        seen_keys = set()
        passage_to_cit_label: List[str] = []
        for idx, p in enumerate(evidence_passages, start=1):
            doc_id = getattr(p, "document_id", "DOC")
            doc_title = getattr(p, "document_title", doc_id) or doc_id
            sec_title = getattr(p, "section_title", "Phần nội dung") or "Phần nội dung"
            para_idx = getattr(p, "paragraph_index", idx)

            key = (doc_id, sec_title, para_idx)
            if key not in seen_keys:
                seen_keys.add(key)
                cit_label = f"[{len(dedup_citations) + 1}]"
                dedup_citations.append({
                    "citation_index": len(dedup_citations) + 1,
                    "citation_label": cit_label,
                    "passage_id": getattr(p, "passage_id", f"PASSAGE_{idx}"),
                    "document_id": doc_id,
                    "document_title": doc_title,
                    "section_title": sec_title,
                    "paragraph_index": para_idx,
                    "score": round(float(getattr(p, "score", 1.0)), 4),
                    "text": getattr(p, "text", "")[:400],
                })
                passage_to_cit_label.append(cit_label)
            else:
                # Find existing label for this key
                matched_lbl = "[1]"
                for dc in dedup_citations:
                    if (dc["document_id"], dc["section_title"], dc["paragraph_index"]) == key:
                        matched_lbl = dc["citation_label"]
                        break
                passage_to_cit_label.append(matched_lbl)

        # Map each sentence in sentence_pool to its passage citation label
        sentence_cit_labels: List[str] = []
        for p_idx, passage in enumerate(evidence_passages):
            passage_text = getattr(passage, "text", "") if hasattr(passage, "text") else str(passage)
            p_lbl = passage_to_cit_label[p_idx] if p_idx < len(passage_to_cit_label) else "[1]"
            for _ in split_sentences(passage_text):
                sentence_cit_labels.append(p_lbl)

        # Check compound query decomposition so multi-part questions cover all sub-queries
        sub_query_sentences: List[Tuple[str, str]] = []
        try:
            from src.reasoning.query_decomposer import QueryDecomposer
            decomp = QueryDecomposer().decompose(query)
            if decomp.is_compound and len(decomp.sub_queries) >= 2:
                for sq in decomp.sub_queries:
                    sq_exp, _ = expand_query_semantics(sq.text)
                    sq_best = select_best_sentence(sq_exp, sentence_pool, sentence_sections)
                    if sq_best and sq_best in sentence_pool:
                        s_idx = sentence_pool.index(sq_best)
                        s_lbl = sentence_cit_labels[s_idx] if s_idx < len(sentence_cit_labels) else "[1]"
                        if all(sq_best != existing_s for existing_s, _ in sub_query_sentences):
                            sub_query_sentences.append((sq_best, s_lbl))
                if sub_query_sentences:
                    best_sentence = sub_query_sentences[0][0]
        except Exception:
            pass

        cit_1 = dedup_citations[0]["citation_label"] if dedup_citations else "[1]"
        if best_sentence in sentence_pool:
            b_idx = sentence_pool.index(best_sentence)
            if b_idx < len(sentence_cit_labels):
                cit_1 = sentence_cit_labels[b_idx]

        # Precision cut: minimal answering span in concise mode, full rich sentence in balanced/detailed
        answer_core = extract_answer_span(exp_query, best_sentence) if best_sentence else ""
        if (
            not answer_core
            or len(answer_core.split()) < 4
            or answer_core.strip().endswith(":")
            or ":" in best_sentence
            or (answer_mode != "concise" and len(answer_core) < len(best_sentence) * 0.75)
        ):
            answer_core = best_sentence

        if answer_core and not answer_core.endswith((".", "!", "?")):
            answer_core += "."

        # Follow-up questions grounded in the evidence that was actually used.
        target_sec_name = dedup_citations[0]["section_title"] if dedup_citations else "chương mục"
        all_context_text = "\n".join(
            getattr(p, "text", "") if hasattr(p, "text") else str(p)
            for p in evidence_passages[:3]
        )
        follow_ups = generate_followup_questions(
            query=query,
            context=all_context_text,
            section_title=target_sec_name,
        )

        if answer_mode == "concise":
            body = f"{answer_core} {cit_1}".strip()
        else:
            from src.self_study.reader import detect_query_intent
            from src.self_study.answer_composer import CoherentAnswerComposer

            intent = detect_query_intent(query)
            composer = CoherentAnswerComposer()

            doc_display_title = dedup_citations[0]["document_title"] if dedup_citations else "tài liệu"
            sec_display_title = dedup_citations[0]["section_title"] if dedup_citations else ""
            sec_part = ""
            if sec_display_title and sec_display_title not in {"Phần nội dung", "Section", "DOC", "Nội dung"}:
                sec_part = f" (mục `{sec_display_title}`)"

            intent_intros = {
                "DEFINITION": f"Theo tài liệu **{doc_display_title}**{sec_part}, khái niệm và bản chất của nội dung này được xác định cụ thể như sau:",
                "MECHANISM": f"Dựa trên phân tích kỹ thuật trong **{doc_display_title}**{sec_part}, cơ chế vận hành và quy trình thực hiện diễn ra như sau:",
                "METRIC": f"Các số liệu định lượng và kết quả thực nghiệm ghi nhận từ **{doc_display_title}**{sec_part} cho thấy:",
                "ENUMERATION": f"Tài liệu **{doc_display_title}**{sec_part} hệ thống hóa các thành phần và nội dung chi tiết bao gồm:",
                "CAUSE": f"Về nguyên nhân và cơ sở lý luận, **{doc_display_title}**{sec_part} phân tích rõ các yếu tố sau:",
                "COMPARISON": f"Khi đối chiếu các khía cạnh trong **{doc_display_title}**{sec_part}, những điểm phân biệt cốt lõi gồm:",
                "LIMITATION": f"Bên cạnh các kết quả đạt được, **{doc_display_title}**{sec_part} cũng chỉ rõ những thách thức và giới hạn kỹ thuật sau:",
                "ADVANTAGE": f"Về hiệu quả và giá trị mang lại, **{doc_display_title}**{sec_part} ghi nhận các điểm nổi bật sau:",
            }
            intro = intent_intros.get(
                intent,
                f"Dựa trên tài liệu **{doc_display_title}**{sec_part}, nội dung được phân tích và tổng hợp như sau:",
            )

            core_line = f"{answer_core} {cit_1}"

            # Collect multi-passage facets: sub-query matches first, then cross-passage insights
            max_facets = 5 if answer_mode == "detailed" else 3
            selected_facets: List[Tuple[str, str]] = []
            used_sents = {best_sentence.strip()}

            for sq_s, sq_lbl in sub_query_sentences:
                if sq_s.strip() not in used_sents:
                    selected_facets.append((sq_s, sq_lbl))
                    used_sents.add(sq_s.strip())

            # First pass: ensure at least 1 high-value sentence from each additional passage [2], [3]...
            for s, lbl in zip(sentence_pool, sentence_cit_labels):
                if len(selected_facets) >= max_facets:
                    break
                if s.strip() not in used_sents and lbl != cit_1:
                    selected_facets.append((s, lbl))
                    used_sents.add(s.strip())

            # Second pass: fill remaining facet slots from any passage
            for s, lbl in zip(sentence_pool, sentence_cit_labels):
                if len(selected_facets) >= max_facets:
                    break
                if s.strip() not in used_sents:
                    selected_facets.append((s, lbl))
                    used_sents.add(s.strip())

            role_labels = {
                "mechanism": "Cơ chế & Kiến trúc",
                "metric": "Số liệu & Thực nghiệm",
                "limitation": "Lưu ý & Giới hạn",
                "elaboration": "Chi tiết triển khai",
            }
            bullet_lines = []
            for f_sent, f_lbl in selected_facets:
                role = composer.classify_sentence_role(f_sent)
                role_title = role_labels.get(role, "Thông tin bổ sung")
                s_clean = f_sent.strip()
                if s_clean and s_clean[-1] not in ".!?":
                    s_clean += "."
                bullet_lines.append(f"- **{role_title}**: {s_clean} {f_lbl}")

            # Automatic Quantitative Delta Reasoner across primary claim & selected facets
            all_used_pairs = [(best_sentence, cit_1)] + selected_facets
            unit_buckets: Dict[str, List[Tuple[float, str, str]]] = {}
            for u_sent, u_lbl in all_used_pairs:
                for nm in re.finditer(
                    r"(\d+(?:[.,]\d+)?)\s*(%|(?:mb|gb|ms|s|tokens?|triệu|tỷ)\b)",
                    u_sent,
                    re.IGNORECASE,
                ):
                    raw_num = nm.group(1).replace(",", ".")
                    unit_key = nm.group(2).lower()
                    try:
                        num_val = float(raw_num)
                    except ValueError:
                        continue
                    unit_buckets.setdefault(unit_key, [])
                    if all(abs(num_val - existing[0]) > 1e-6 for existing in unit_buckets[unit_key]):
                        unit_buckets[unit_key].append((num_val, nm.group(0).strip(), u_lbl))

            for unit_key, entries in unit_buckets.items():
                if len(entries) >= 2:
                    v1, raw1, lbl1 = entries[0]
                    v2, raw2, lbl2 = entries[1]
                    delta_val = round(abs(v1 - v2), 2)
                    delta_str = f"{delta_val:g}"
                    unit_disp = "%" if unit_key == "%" else f" { entries[0][1].split()[-1] if ' ' in entries[0][1] else unit_key }"
                    cit_pair = lbl1 if lbl1 == lbl2 else f"{lbl1} {lbl2}"
                    bullet_lines.append(
                        f"- **Đối chiếu định lượng tự động**: Mức chênh lệch giữa hai mốc số liệu được ghi nhận là **{delta_str}{unit_disp}** ({raw1} so với {raw2}). {cit_pair}"
                    )
                    break

            parts = [f"{intro}\n\n{core_line}"]
            if bullet_lines:
                parts.append("📌 **Phân tích đa chiều từ tài liệu:**\n" + "\n".join(bullet_lines))

            if answer_mode == "detailed":
                # Defense Strategist integration (Wave 3)
                try:
                    from src.brain.defense_strategist import DefenseStrategist
                    strategist = DefenseStrategist()
                    plan = strategist.plan(query)
                    if plan.archetype != "GENERIC" and plan.confidence >= 0.35:
                        cand_dicts = [
                            {
                                "sentence": s,
                                "citation_label": lbl,
                                "section_title": sec,
                            }
                            for s, lbl, sec in zip(sentence_pool, sentence_cit_labels, sentence_sections)
                        ]
                        arg_block = strategist.assemble_argument(plan, cand_dicts)
                        if arg_block and "- **" in arg_block:
                            parts.append(arg_block)
                except Exception:
                    pass

                sec_list = sorted({c["section_title"] for c in dedup_citations if c.get("section_title")})
                sec_summary = ", ".join(f"`{s}`" for s in sec_list[:3]) if sec_list else f"**{doc_display_title}**"
                cit_badges = " ".join(c["citation_label"] for c in dedup_citations[:3])
                parts.append(
                    f"💡 **Tổng hợp & Đúc kết chuyên sâu:**\n"
                    f"Nội dung trên được tổng hợp đối chiếu trực tiếp từ {len(dedup_citations)} đoạn chứng cứ thuộc {sec_summary} "
                    f"trong tài liệu **{doc_display_title}** {cit_badges}, bảo đảm tính toàn vẹn ngữ cảnh và không suy diễn ngoài văn bản."
                )

            body = "\n\n".join(parts)

        # Sources first, then the mandatory trailing question block.
        sources_lines = [
            f"{c['citation_label']} **{c['document_title']}** — {c['section_title']} — Đoạn {c['paragraph_index']}"
            for c in dedup_citations[:3]
        ]

        body = strip_question_block(body)
        if sources_lines:
            body = f"{body}\n\n### Nguồn tham khảo\n" + "\n\n".join(sources_lines)

        full_answer = ensure_trailing_question(body, follow_ups)
        return full_answer, dedup_citations
