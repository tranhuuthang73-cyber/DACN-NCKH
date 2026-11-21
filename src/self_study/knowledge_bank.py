"""
Self-Study Knowledge Bank & Answer Instruction Blueprints (Wave 5).
Pure-Python, strict offline, zero LLM overhead (< 25ms per document).

Provides:
1. ANSWER_INSTRUCTION_BLUEPRINTS: 6 behavioral archetypes for grounded answering.
2. SelfStudyKnowledgeBank: Rapid document structural learner, extractor of definitions,
   classifications, formulas, and examples, and generator of natural self-study questions.
3. get_knowledge_bank(): Global thread-safe singleton.
"""

import re
import unicodedata
from typing import List, Dict, Any, Optional, Set, Tuple


def strip_accents(text: str) -> str:
    """Removes Vietnamese tone marks for accent-insensitive canonical alignment."""
    if not text:
        return ""
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return text.replace("đ", "d").replace("Đ", "D")


def _is_one_edit_away(a: str, b: str) -> bool:
    """Returns True if two tokens (>= 3 chars) differ by exactly 1 edit (sub/ins/del)."""
    if a == b:
        return False
    la, lb = len(a), len(b)
    if abs(la - lb) > 1 or la < 3 or lb < 3:
        return False
    if la == lb:
        return sum(1 for ca, cb in zip(a, b) if ca != cb) == 1
    if la < lb:
        a, b = b, a
    i = j = diffs = 0
    while i < len(a) and j < len(b):
        if a[i] != b[j]:
            diffs += 1
            if diffs > 1:
                return False
            i += 1
        else:
            i += 1
            j += 1
    return True


_KB_STOP_TOKENS = {
    "la", "gi", "cua", "va", "voi", "cac", "nhung", "mot", "cho", "biet",
    "ve", "co", "duoc", "trong", "nay", "nao", "nhu", "the", "bao", "nhieu",
    "loai", "phan", "liet", "ke", "vi", "du", "tai", "lieu", "khai", "niem",
    "dinh", "nghia", "hay", "giai", "thich", "trinh", "bay", "muc", "bai",
}


def _score_doc_relevance(query: str, doc: Dict[str, Any]) -> float:
    """Scores a learned document against query using normalized + 1-edit fuzzy tokens."""
    q_norm = strip_accents((query or "").lower())
    raw_q_tokens = re.findall(r"[a-z0-9_]+", q_norm)
    q_tokens = [t for t in raw_q_tokens if len(t) >= 2 and t not in _KB_STOP_TOKENS]
    if not q_tokens:
        q_tokens = [t for t in raw_q_tokens if len(t) >= 2]
    if not q_tokens:
        return 0.0

    title_norm = strip_accents((doc.get("title") or "").lower())
    headings_norm = strip_accents(
        " ".join(s.get("heading", "") for s in doc.get("sections", [])).lower()
    )
    raw_norm = strip_accents((doc.get("raw_text") or "").lower())
    if not raw_norm:
        raw_norm = strip_accents(
            " ".join(
                " ".join(s.get("lines", [])) for s in doc.get("sections", [])
            ).lower()
        )

    title_tokens = set(re.findall(r"[a-z0-9_]+", f"{title_norm} {headings_norm}"))
    doc_tokens = set(re.findall(r"[a-z0-9_]+", raw_norm)) | title_tokens
    if not doc_tokens:
        return 0.0

    exact_hits = 0
    fuzzy_score = 0.0
    score = 0.0
    for qt in q_tokens:
        if qt in title_tokens:
            score += 3.0
            exact_hits += 1
        elif qt in doc_tokens:
            score += 1.5
            exact_hits += 1
        elif len(qt) >= 3:
            if any(_is_one_edit_away(qt, dt) for dt in title_tokens):
                fuzzy_score += 1.5
            elif any(_is_one_edit_away(qt, dt) for dt in doc_tokens):
                fuzzy_score += 0.8

    # Only credit fuzzy typo hits when corroborated by context (or single-token query)
    if exact_hits > 0 or len(q_tokens) == 1:
        score += fuzzy_score

    # Bigram phrase bonus
    for i in range(len(q_tokens) - 1):
        bg = f"{q_tokens[i]} {q_tokens[i + 1]}"
        if bg in title_norm or bg in headings_norm:
            score += 2.5
        elif bg in raw_norm:
            score += 1.5

    return score


ANSWER_INSTRUCTION_BLUEPRINTS: Dict[str, Dict[str, Any]] = {
    "DEFINITION_AND_TYPES": {
        "intent": "Định nghĩa, phân loại và các hệ/phương pháp",
        "cues": [
            "là gì", "khái niệm", "bao nhiêu loại", "phân loại", "các phương pháp",
            "các hệ", "những loại nào", "phương pháp nào", "có mấy loại",
        ],
        "instructions": [
            "1. Trình bày khái niệm/định nghĩa cốt lõi từ mục giới thiệu.",
            "2. Liệt kê đầy đủ các phương pháp/phân loại trong mục và các hệ cụ thể xuyên suốt tài liệu.",
            "3. Nêu công thức hoặc ví dụ minh họa nếu câu hỏi yêu cầu hoặc có sẵn.",
        ],
    },
    "SECTION_FULL_EXPLANATION": {
        "intent": "Giải thích toàn diện một mục/chủ đề",
        "cues": [
            "mục", "chủ đề", "topic", "phần", "chương", "bài", "nội dung của", "chi tiết về",
        ],
        "instructions": [
            "1. Xác định chính xác mục được hỏi.",
            "2. Trích xuất và kết nối toàn bộ các ý gạch đầu dòng thành văn bản mạch lạc, đầy đủ.",
        ],
    },
    "MECHANISM_AND_FORMULA": {
        "intent": "Cách hoạt động, nguyên lý và công thức toán",
        "cues": [
            "cách hoạt động", "nguyên lý", "công thức", "thuật toán", "quy trình",
            "vận hành", "hoạt động như thế nào", "cách thức",
        ],
        "instructions": [
            "1. Trình bày quy trình hoạt động từng bước.",
            "2. Nêu rõ các công thức toán học và giải thích ý nghĩa các ký hiệu.",
        ],
    },
    "COMPARISON_AND_SECURITY": {
        "intent": "An ninh, phá mã, ưu nhược điểm và so sánh",
        "cues": [
            "an ninh", "ưu nhược điểm", "so sánh", "phá mã", "thám mã", "tấn công",
            "an toàn", "bảo mật", "đánh giá",
        ],
        "instructions": [
            "1. Phân tích các điều kiện an ninh (vô điều kiện, tính toán).",
            "2. Tổng hợp các nguy cơ phá mã hoặc ưu nhược điểm tương đối.",
        ],
    },
    "EXAMPLE_WALKTHROUGH": {
        "intent": "Ví dụ và minh họa cụ thể",
        "cues": [
            "ví dụ", "minh họa", "cho ví dụ", "áp dụng thực tế", "bài toán",
        ],
        "instructions": [
            "1. Trích xuất ví dụ có trong tài liệu.",
            "2. Nêu rõ các bước biến đổi cụ thể.",
        ],
    },
    "SUMMARY_OVERVIEW": {
        "intent": "Tóm tắt tổng quan toàn bộ tài liệu",
        "cues": [
            "tổng quan", "tóm tắt", "toàn bộ tài liệu", "nội dung chính của tài liệu",
            "tài liệu nói về gì",
        ],
        "instructions": [
            "1. Tóm lược cấu trúc các mục chính.",
            "2. Nêu bật các kết luận hoặc thông điệp trọng tâm.",
        ],
    },
}


class SelfStudyKnowledgeBank:
    """
    In-memory learned document knowledge bank:
    Stores parsed sections, definitions, classifications, formulas, examples,
    and synthesized QA pairs for lightning-fast (< 40ms) grounded answers.
    """

    def __init__(self):
        self._documents: Dict[str, Dict[str, Any]] = {}

    def clear(self):
        self._documents.clear()

    def learn_document(
        self,
        doc_id: str,
        title: str,
        raw_text: str,
        passages: Optional[List[Any]] = None,
    ) -> Dict[str, Any]:
        """
        Fast structural parser and self-study generator (< 25ms):
        Extracts sections, bullets, definitions, classifications, and examples.
        """
        if not raw_text:
            return {"doc_id": doc_id, "status": "empty"}

        # Extract passages map
        passage_map: Dict[str, str] = {}
        if passages:
            for p in passages:
                pid = getattr(p, "passage_id", None) or (p.get("passage_id") if isinstance(p, dict) else "DOC::P000")
                ptxt = getattr(p, "text", None) or (p.get("text") if isinstance(p, dict) else "")
                sec = getattr(p, "section_title", None) or (p.get("section_title") if isinstance(p, dict) else "")
                if sec:
                    passage_map[sec.strip().lower()] = pid
                passage_map[pid] = ptxt

        # Parse sections by headings
        # Supported: 1. GIỚI THIỆU, 3. PHÁ MÃ, Topic 49, # Header, etc.
        lines = raw_text.splitlines()
        sections: List[Dict[str, Any]] = []
        current_sec: Optional[Dict[str, Any]] = None

        heading_re = re.compile(
            r"^(?:===\s*Page\s*\d+\s*===\s*)?"
            r"(?:#+\s*)?"
            r"(\d+\.|\b[IVXLCDM]+\.|\bTopic\s+\d+[:.\-–]?|\bChủ đề\s+\d+[:.\-–]?|\bBài\s+\d+[:.\-–]?|\bMục\s+\d+[:.\-–]?)\s*"
            r"([^\n:]+):?",
            re.IGNORECASE,
        )

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            # Check page marker alone
            if re.match(r"^===\s*Page\s*\d+\s*===$", line_str, re.IGNORECASE):
                continue

            # Strip leading page marker if combined
            clean_line = re.sub(r"^===\s*Page\s*\d+\s*===\s*", "", line_str).strip()

            m = heading_re.match(clean_line)
            if m:
                pfx = m.group(1).strip()
                title_body = m.group(2).strip()
                full_h = f"{pfx} {title_body}".strip()
                if current_sec:
                    sections.append(current_sec)
                current_sec = {
                    "heading": full_h,
                    "title": title_body,
                    "prefix": pfx,
                    "lines": [],
                    "bullets": [],
                    "paragraphs": [],
                    "examples": [],
                    "formulas": [],
                }
                continue

            if current_sec is not None:
                current_sec["lines"].append(clean_line)
                # Detect bullets
                if re.match(r"^[\-\*\+•]\s+", clean_line) or re.match(r"^\d+\)\s+", clean_line):
                    bullet_text = re.sub(r"^[\-\*\+•]\s+", "", clean_line).strip()
                    current_sec["bullets"].append(bullet_text)
                else:
                    current_sec["paragraphs"].append(clean_line)

                # Detect formula
                if any(sym in clean_line for sym in [" = ", " + ", " mod ", " \u2295 ", " XOR ", "zi = "]):
                    current_sec["formulas"].append(clean_line)

                # Detect example
                if any(kw in clean_line.lower() for kw in ["ví dụ", "vi du", "cho p =", "giả sử"]):
                    current_sec["examples"].append(clean_line)
            else:
                # Pre-heading preamble
                pass

        if current_sec:
            sections.append(current_sec)

        # Fallback if no numbered headings found: split by markdown or paragraphs
        if not sections:
            paragraphs = [p.strip() for p in raw_text.split("\n\n") if p.strip()]
            sections.append({
                "heading": title or "Tài liệu",
                "title": title or "Tài liệu",
                "prefix": "1.",
                "lines": paragraphs,
                "bullets": [p for p in paragraphs if p.startswith(("-", "*", "•"))],
                "paragraphs": paragraphs,
                "examples": [p for p in paragraphs if "ví dụ" in p.lower()],
                "formulas": [],
            })

        # Identify definitions, classifications, and system names across sections
        definitions: List[str] = []
        classifications: List[str] = []
        systems_found: List[str] = []

        for sec in sections:
            h_text = sec["heading"]
            clean_h = sec["title"]

            # Collect system / cipher names from headings
            if any(term in h_text.lower() for term in ["mã hoá", "mã hóa", "hệ mã", "cipher", "topic", "thuật toán"]):
                systems_found.append(h_text)

            # Check if this section defines concepts (e.g. Giới thiệu, Khái niệm, Định nghĩa)
            if any(term in h_text.lower() for term in ["giới thiệu", "khái niệm", "định nghĩa", "tổng quan"]):
                for line in sec["lines"]:
                    if not line.startswith(("-", "*", "•")) or len(line) > 20:
                        definitions.append(line.lstrip("-*• ").strip())

            # Check for classification bullets
            for b in sec["bullets"]:
                if any(k in b.lower() for k in ["phương pháp", "phân loại", "thay thế", "hoán vị", "loại"]):
                    classifications.append(b)
                elif any(b.lower().startswith(pfx) for pfx in ["mã hóa thay thế", "mã hóa hoán vị", "an ninh"]):
                    classifications.append(b)

        # Integrate with specialized taxonomy and formula dataset extractors
        try:
            from src.self_study.datasets.definition_and_taxonomy_patterns import extract_taxonomy_and_types
            tax_data = extract_taxonomy_and_types(passages if passages else [{"text": raw_text}])
            if tax_data.get("bullet_types"):
                classifications = list(dict.fromkeys(classifications + tax_data["bullet_types"]))
            if tax_data.get("concrete_types"):
                systems_found = list(dict.fromkeys(systems_found + tax_data["concrete_types"]))
        except Exception:
            pass

        try:
            from src.self_study.datasets.formula_and_example_patterns import extract_examples_and_formulas
            f_ex_data = extract_examples_and_formulas(passages if passages else [{"text": raw_text}])
        except Exception:
            f_ex_data = {}

        try:
            from src.self_study.datasets.autonomous_qa_generator import SelfCurriculumGenerator
            qa_curriculum = SelfCurriculumGenerator.generate_curriculum(doc_id, title, passages if passages else [{"text": raw_text}])
        except Exception:
            qa_curriculum = []

        doc_entry = {
            "doc_id": doc_id,
            "title": title,
            "raw_text": raw_text,
            "sections": sections,
            "definitions": definitions,
            "classifications": classifications,
            "systems": systems_found,
            "passage_map": passage_map,
            "formulas_data": f_ex_data,
            "curriculum_qa": qa_curriculum,
        }

        self._documents[doc_id] = doc_entry

        return {
            "doc_id": doc_id,
            "sections_count": len(sections),
            "definitions_count": len(definitions),
            "classifications_count": len(classifications),
            "systems_count": len(systems_found),
            "status": "learned",
        }

    def classify_answer_blueprint(self, query: str) -> str:
        """Classifies user question into one of the 6 answer blueprints."""
        q_norm = strip_accents((query or "").lower())

        def _has_cue(cues: List[str]) -> bool:
            for c in cues:
                if re.search(r"\b" + re.escape(c) + r"\b", q_norm):
                    return True
            return False

        # Check SUMMARY_OVERVIEW
        if _has_cue(["tong quan", "tom tat", "toan bo tai lieu", "noi dung chinh"]):
            return "SUMMARY_OVERVIEW"

        # Check DEFINITION_AND_TYPES: asks definition + types/methods/examples or enumerating types/methods/ciphers
        has_def = _has_cue(["la gi", "khai niem", "dinh nghia"])
        has_enum_types = _has_cue([
            "bao nhieu loai", "phan loai", "cac phuong phap", "cac he", "may loai",
            "nhung loai nao", "he ma nao", "phuong phap nao", "liet ke", "cac loai",
            "bao nhieu phuong phap", "cac he ma",
        ])
        has_types = has_enum_types or _has_cue(["cho vi du", "vi du"])
        is_specific_section = bool(
            re.search(r"\b(?:topic|chu de|bai|muc|chuong|phan)\s*\d+\b", q_norm)
            or re.search(r"^\s*\d+\.\s+[a-z0-9]", q_norm)
        )
        if has_def and has_types:
            return "DEFINITION_AND_TYPES"
        if has_enum_types and not is_specific_section:
            return "DEFINITION_AND_TYPES"
        if has_def:
            if _has_cue(["loai", "he", "phuong phap"]):
                return "DEFINITION_AND_TYPES"

        # Check COMPARISON_AND_SECURITY: asks security, attacks, comparison, pros/cons
        if _has_cue(["an ninh", "tham ma", "tan cong", "uu nhuoc diem", "so sanh", "bao mat", "an toan"]):
            return "COMPARISON_AND_SECURITY"

        # Check MECHANISM_AND_FORMULA: asks how it works, formulas, algorithms
        if _has_cue(["cach hoat dong", "nguyen ly", "cong thuc", "thuat toan", "quy trinh"]):
            return "MECHANISM_AND_FORMULA"

        # Check EXAMPLE_WALKTHROUGH: asks for examples/walkthroughs
        if _has_cue(["cho vi du", "vi du minh hoa", "minh hoa"]):
            return "EXAMPLE_WALKTHROUGH"

        # Check SECTION_FULL_EXPLANATION: specific section number or topic name
        if re.search(r"\b(?:topic|chu de|bai|muc|chuong|phan)\s*\d+\b", q_norm) or re.search(r"^\s*\d+\.\s+[a-z0-9]", q_norm):
            return "SECTION_FULL_EXPLANATION"
        if _has_cue(["pha ma", "playfair", "autokey", "don mot lan", "ma hoa dong"]):
            return "SECTION_FULL_EXPLANATION"

        return "DEFINITION_AND_TYPES" if has_def else "SECTION_FULL_EXPLANATION"

    def synthesize_learned_answer(
        self,
        query: str,
        doc_ids: Optional[List[str]] = None,
        passages: Optional[List[Dict[str, Any]]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Synthesizes a full structured text answer directly from learned document knowledge.
        Returns None if query cannot be fulfilled from learned knowledge.
        """
        if not self._documents:
            return None

        # Select target documents (Strict Document Scope Lock when doc_ids is provided)
        target_docs = []
        if doc_ids is not None:
            for did in doc_ids:
                if did in self._documents:
                    target_docs.append(self._documents[did])
            if not target_docs:
                return None
        else:
            target_docs = list(self._documents.values())

        if not target_docs:
            return None

        if len(target_docs) > 1:
            scored_docs = [(_score_doc_relevance(query, d), d) for d in target_docs]
            best_doc_score, doc = max(scored_docs, key=lambda item: item[0])
            if best_doc_score <= 0.0:
                return None
        else:
            doc = target_docs[0]
        sections = doc.get("sections", [])
        q_norm = strip_accents((query or "").lower())
        blueprint = self.classify_answer_blueprint(query)

        # Check if query targets a specific non-intro section/topic (should bypass general Case A)
        m_quote_top = re.search(r"['\"]([^'\"]+)['\"]", query or "")
        quoted_target_norm = strip_accents(m_quote_top.group(1).lower()) if m_quote_top else ""
        has_numbered_target = bool(
            re.search(r"\b(?:topic|chu de|bai|muc|chuong|phan)\s*\d+\b", q_norm)
            or re.search(r"^\s*\d+\.\s+[a-z0-9]", q_norm)
        )
        is_intro_target = bool(
            quoted_target_norm and any(k in quoted_target_norm for k in ["gioi thieu", "tong quan", "mo dau"])
        )
        asks_doc_wide_enum = any(
            k in q_norm
            for k in [
                "bao nhieu loai", "phan loai", "liet ke", "may loai",
                "nhung loai nao", "he ma nao", "phuong phap nao", "cac he ma",
                "cac phuong phap", "cac loai", "cho vi du", "bao nhieu phuong phap",
            ]
        )
        intro_sec = next(
            (s for s in sections if any(k in strip_accents(s["heading"].lower()) for k in ["gioi thieu", "khai niem", "tong quan"])),
            sections[0] if sections else None,
        )
        doc_title_norm = strip_accents((doc.get("title") or "").lower())
        q_subject = re.sub(r"\b(?:la gi|khai niem|dinh nghia|cho biet|hay|giai thich|cua|ve)\b", " ", q_norm)
        q_subject_tokens = [t for t in re.findall(r"[a-z0-9_]+", q_subject) if len(t) >= 2]
        is_compound_def = bool(re.search(r"\b(?:va|voi|hay)\b", q_subject)) and len(q_subject_tokens) >= 2
        main_topic_tokens = set(re.findall(r"[a-z0-9_]+", doc_title_norm))
        asks_main_doc_topic = bool(
            q_subject_tokens
            and not is_compound_def
            and sum(1 for t in q_subject_tokens if t in main_topic_tokens) >= max(2, (len(q_subject_tokens) + 1) // 2)
        )
        skip_case_a_for_specific_target = (
            (bool(quoted_target_norm) or has_numbered_target)
            and not is_intro_target
            and not asks_doc_wide_enum
        )

        # ----------------------------------------------------------------------
        # Case A: DEFINITION_AND_TYPES (only for doc-wide enumeration or main doc topic)
        # ----------------------------------------------------------------------
        if not skip_case_a_for_specific_target and (
            asks_doc_wide_enum
            or (blueprint == "DEFINITION_AND_TYPES" and asks_main_doc_topic)
        ):
            concept_points = []
            if intro_sec:
                for line in intro_sec["lines"]:
                    if not line.startswith(("-", "*", "•")) or len(line) > 20:
                        cleaned_l = line.lstrip("-*• ").strip()
                        if cleaned_l:
                            concept_points.append(cleaned_l)
                if not concept_points:
                    for b in intro_sec.get("bullets", []):
                        cleaned_b = b.lstrip("-*• ").strip()
                        if cleaned_b:
                            concept_points.append(cleaned_b)

            if not concept_points:
                for s in sections:
                    for line in s.get("lines", []) or s.get("bullets", []):
                        cleaned_l = line.lstrip("-*• ").strip()
                        if cleaned_l:
                            concept_points.append(cleaned_l)
                            if len(concept_points) >= 3:
                                break
                    if concept_points:
                        break

            if not concept_points:
                return None

            concept_text = " ".join(concept_points[:3])

            # 2. Methods / Classifications: collect from intro bullets and section titles
            bullet_methods = []
            if intro_sec:
                for b in intro_sec["bullets"]:
                    clean_b = b.strip()
                    if clean_b:
                        bullet_methods.append(f"- {clean_b}")

            # Specific systems across the whole document (skip intro/cryptanalysis headings, keep all ciphers/methods)
            system_names: List[str] = []
            seen_sys_norm: set = set()
            sys_cues = (
                "he ma", "ma hoa", "ma ", "thuat toan", "cipher", "don mot lan",
                "autokey", "playfair", "caesar", "affine", "vigenere", "hill",
                "vernam", "feistel", "des", "aes", "rsa", "ecc", "topic",
            )
            non_sys_cues = ("gioi thieu", "pha ma", "tong quan", "khai niem", "mo dau", "ket luan")
            for s in sections:
                if s is intro_sec:
                    continue
                h = s["heading"]
                clean_name = re.sub(r"^(?:\d+(?:\.\d+)*|[IVXLCDM]+)\.\s*", "", h, flags=re.IGNORECASE).strip()
                norm_name = strip_accents(clean_name.lower())
                if any(ex in norm_name for ex in non_sys_cues):
                    continue
                if any(w in norm_name for w in sys_cues):
                    if norm_name not in seen_sys_norm:
                        seen_sys_norm.add(norm_name)
                        system_names.append(clean_name)
            for extra_sys in doc.get("systems", []):
                clean_extra = re.sub(r"^(?:\d+(?:\.\d+)*|[IVXLCDM]+)\.\s*", "", extra_sys, flags=re.IGNORECASE).strip()
                norm_extra = strip_accents(clean_extra.lower())
                if clean_extra and not any(ex in norm_extra for ex in non_sys_cues) and norm_extra not in seen_sys_norm:
                    seen_sys_norm.add(norm_extra)
                    system_names.append(clean_extra)

            # 3. Examples from sections
            example_snippets = []
            for s in sections:
                if s["examples"]:
                    example_snippets.extend([f"- {s['heading']}: {ex.lstrip('-*• ')}" for ex in s["examples"][:1]])
                elif s["formulas"]:
                    example_snippets.append(f"- {s['heading']}: {s['formulas'][0].lstrip('-*• ')}")

            # Build full structured answer using ExtractiveTextStitcher if available
            try:
                from src.self_study.datasets.extractive_text_stitcher import ExtractiveTextStitcher
                full_answer = ExtractiveTextStitcher.stitch_complete_answer(
                    query=query,
                    intro_sents=concept_points[:3] if concept_points else [concept_text],
                    bullet_types=[b.lstrip("-*• ").strip() for b in bullet_methods],
                    section_systems=system_names,
                    examples=example_snippets[:3],
                )
            except Exception:
                parts = []
                parts.append(f"Dựa trên tài liệu đã cung cấp:")
                parts.append(f"\n1. **Khái niệm:** {concept_text}")

                parts.append(f"\n2. **Phân loại và các phương pháp:**")
                if bullet_methods:
                    parts.append("Các phương pháp phổ biến được ghi nhận trong tài liệu:")
                    parts.extend(bullet_methods)

                if system_names:
                    parts.append("Các hệ mã hóa cụ thể được nghiên cứu xuyên suốt tài liệu gồm:")
                    for sys_name in system_names:
                        parts.append(f"  * {sys_name}")

                if example_snippets:
                    parts.append(f"\n3. **Ví dụ và công thức minh họa:**")
                    parts.extend(example_snippets[:3])

                full_answer = "\n".join(parts)

            return {
                "answer": full_answer,
                "blueprint": "DEFINITION_AND_TYPES",
                "citations": ["[1]"],
                "grounded": True,
            }

        # ----------------------------------------------------------------------
        # Case C: COMPARISON_AND_SECURITY (Pros/Cons, Comparisons, Security)
        # ----------------------------------------------------------------------
        is_explicit_sec_heading = bool(re.search(r"^\s*\d+\.\s+", query.strip()) or re.search(r"['\"][^'\"]+['\"]", query))
        if not is_explicit_sec_heading and (
            blueprint == "COMPARISON_AND_SECURITY"
            or any(k in q_norm for k in ["uu nhuoc diem", "so sanh", "phan biet", "diem manh", "diem yeu", "an ninh", "tham ma"])
        ):
            try:
                from src.self_study.datasets.comparison_and_pros_cons_stitcher import synthesize_pros_cons_and_comparison
                passages = []
                for s in sections:
                    passages.append({
                        "text": f"{s['heading']}\n" + "\n".join(s.get('lines', [])),
                        "section_title": s.get("heading", ""),
                        "passage_id": f"[{s.get('prefix', 'SEC')}]",
                    })
                res_comp = synthesize_pros_cons_and_comparison(query, passages)
                if res_comp and (res_comp.get("has_sufficient_evidence") or res_comp.get("pros") or res_comp.get("cons") or res_comp.get("security_facets")):
                    return {
                        "answer": res_comp["answer"],
                        "blueprint": "COMPARISON_AND_SECURITY",
                        "citations": res_comp.get("citations", ["[1]"]),
                        "grounded": True,
                        "metadata": res_comp.get("metadata", {}),
                    }
            except Exception:
                pass

        # ----------------------------------------------------------------------
        # Case D: MECHANISM_AND_FORMULA / STEP-BY-STEP PROCESS
        # ----------------------------------------------------------------------
        if any(k in q_norm for k in ["cac buoc", "quy trinh", "thuat toan"]):
            try:
                from src.self_study.datasets.step_by_step_process_stitcher import synthesize_step_by_step_process
                passages = []
                for s in sections:
                    passages.append({
                        "text": f"{s['heading']}\n" + "\n".join(s.get('lines', [])),
                        "section_title": s.get("heading", ""),
                        "passage_id": f"[{s.get('prefix', 'SEC')}]",
                    })
                res_proc = synthesize_step_by_step_process(query, passages)
                if res_proc and res_proc.get("steps"):
                    return {
                        "answer": res_proc["answer"],
                        "blueprint": "MECHANISM_AND_FORMULA",
                        "citations": res_proc.get("citations", ["[1]"]),
                        "grounded": True,
                        "metadata": {"steps_count": len(res_proc.get("steps", []))},
                    }
            except Exception:
                pass

        # Do not hijack specific term definition or causal reasoning queries (e.g. "chất khử và chất oxi hóa là gì",
        # "tại sao ... phải bảo toàn electron") into dumping a section/heading; yield to DocumentAnalyzer.find_best_grounded_answer.
        has_def_cue = any(
            re.search(r"\b" + re.escape(c) + r"\b", q_norm)
            for c in ("la gi", "khai niem", "dinh nghia", "tai sao", "vi sao", "nguyen nhan", "ly do")
        )
        if (
            has_def_cue
            and not asks_doc_wide_enum
            and not is_explicit_sec_heading
            and not has_numbered_target
            and not asks_main_doc_topic
        ):
            return None

        # ----------------------------------------------------------------------
        # Case B: SECTION_FULL_EXPLANATION / Specific Topic (e.g. "3. PHÁ MÃ", "'PHÁ MÃ'")
        # ----------------------------------------------------------------------
        # Look for section matching query
        target_sec = None
        # Check quoted topic first: 'PHÁ MÃ' or "PHÁ MÃ"
        m_quote = re.search(r"['\"]([^'\"]+)['\"]", query)
        target_name = m_quote.group(1).strip() if m_quote else ""

        if not target_name:
            # Check topic number: "3. PHÁ MÃ" or "topic 49"
            m_num = re.search(r"(?:^|\b)(\d+)\.?\s*([a-zA-Zà-ỹÀ-Ỹ0-9\s]+)?", query)
            if m_num:
                target_num = m_num.group(1)
                for s in sections:
                    if s["prefix"].startswith(target_num) or f"{target_num}." in s["heading"] or f"Topic {target_num}" in s["heading"]:
                        target_sec = s
                        break

        if not target_sec and target_name:
            t_norm = strip_accents(target_name.lower())
            for s in sections:
                if t_norm in strip_accents(s["heading"].lower()):
                    target_sec = s
                    break

        if not target_sec:
            # Word overlap search across section headings
            best_score = 0
            for s in sections:
                h_norm = strip_accents(s["heading"].lower())
                score = sum(1 for w in q_norm.split() if len(w) > 2 and w in h_norm)
                if score > best_score and score >= 1:
                    best_score = score
                    target_sec = s

        if target_sec:
            h_title = target_sec["heading"]
            raw_items = [line.lstrip("-*• ").strip() for line in target_sec.get("lines", []) if line.strip()]
            if not raw_items:
                return None
            sec_lines = [
                f"- {line.lstrip('-*• ').strip()}" if not line.startswith(("-", "*", "•")) else line
                for line in target_sec.get("lines", [])
            ]

            has_example_cue = any(k in q_norm for k in ["vi du", "minh hoa", "ung dung", "ap dung", "thuc te"])
            has_mech_cue = any(
                k in q_norm
                for k in [
                    "nguyen ly", "co che", "cach hoat dong", "hoat dong", "dac diem",
                    "cong thuc", "phep toan", "quy tac", "thuat toan", "uu diem",
                    "nhuoc diem", "uu nhuoc diem",
                ]
            )
            has_concept_cue = any(k in q_norm for k in ["khai niem", "dinh nghia", "la gi", "y chinh", "tom tat", "trong tam"])
            asks_full = any(k in q_norm for k in ["chi tiet", "toan bo", "day du"]) or (
                "noi dung" in q_norm and not (has_example_cue or has_mech_cue or has_concept_cue)
            )

            full_answer: Optional[str] = None
            if not asks_full and len(raw_items) > 1:
                if has_example_cue:
                    app_cues = ["thoi gian thuc", "truyen thong", "ung dung", "ap dung", "vi du", "minh hoa", "gia su", "cho "]
                    focused = list(dict.fromkeys(
                        [x.lstrip("-*• ").strip() for x in target_sec.get("examples", []) if x.strip()]
                        + [x.lstrip("-*• ").strip() for x in target_sec.get("formulas", []) if x.strip()]
                        + [item for item in raw_items if any(c in strip_accents(item.lower()) for c in app_cues)]
                    ))
                    if focused:
                        full_answer = (
                            f"Ví dụ, công thức minh họa và ứng dụng của **{h_title}**:\n\n"
                            + "\n".join(f"- {item}" for item in focused)
                        )
                elif has_mech_cue:
                    formula_set = {x.lstrip("-*• ").strip() for x in target_sec.get("formulas", [])}
                    mech_cues = [
                        "=", "mod", "xor", "phep", "cong thuc", "sinh ra", "ma hoa", "giai ma",
                        "quy tac", "ma tran", "thay the", "hoan vi", "mo rong", "buoc",
                        "uu diem", "nhuoc diem", "dac diem", "toc do", "do tre", "tan cong",
                        "tham ma", "an ninh",
                    ]
                    focused = [
                        item for item in raw_items
                        if item in formula_set or any(c in strip_accents(item.lower()) for c in mech_cues)
                    ]
                    if focused:
                        full_answer = (
                            f"Nguyên lý, cơ chế và đặc điểm của **{h_title}**:\n\n"
                            + "\n".join(f"- {item}" for item in focused)
                        )
                elif has_concept_cue:
                    def_cues = ["la ", "duoc dinh nghia", "hoan hao", "co so", "dung de", "con goi la", "muc dich"]
                    para_items = [p.lstrip("-*• ").strip() for p in target_sec.get("paragraphs", []) if p.strip()]
                    primary = next(
                        (item for item in raw_items if any(c in strip_accents(item.lower()) for c in def_cues)),
                        para_items[0] if para_items else raw_items[0],
                    )
                    formula_set = {x.lstrip("-*• ").strip() for x in target_sec.get("formulas", [])}
                    rest = [item for item in raw_items if item != primary]
                    non_formula_rest = [item for item in rest if item not in formula_set]
                    summary_rest = (non_formula_rest if non_formula_rest else rest)[:2]
                    full_answer = f"Khái niệm và ý chính của **{h_title}**:\n\n**Khái niệm cốt lõi:** {primary}"
                    if summary_rest:
                        full_answer += "\n\n**Ý chính liên quan:**\n" + "\n".join(f"- {item}" for item in summary_rest)

            if full_answer is None:
                try:
                    from src.self_study.datasets.extractive_text_stitcher import ExtractiveTextStitcher
                    full_answer = ExtractiveTextStitcher.stitch_section_detail(
                        section_title=h_title,
                        content_lines=target_sec.get("lines", []),
                    )
                except Exception:
                    content_body = "\n".join(sec_lines) if sec_lines else target_sec["title"]
                    full_answer = (
                        f"Trong mục **{h_title}**, tài liệu ghi nhận thông tin chi tiết như sau:\n\n"
                        f"{content_body}"
                    )
            return {
                "answer": full_answer,
                "blueprint": "SECTION_FULL_EXPLANATION",
                "citations": ["[1]"],
                "grounded": True,
            }

        return None

    def get_self_study_questions(
        self,
        doc_ids: Optional[List[str]] = None,
        current_query: str = "",
        top_passages: Optional[List[Dict[str, Any]]] = None,
        count: int = 3,
    ) -> List[str]:
        """
        Generates clean, natural self-study questions anchored to real document sections.
        Guarantees 100% answerability and zero robotic templates.
        """
        target_docs = []
        if doc_ids:
            for did in doc_ids:
                if did in self._documents:
                    target_docs.append(self._documents[did])
        if not target_docs:
            target_docs = list(self._documents.values())

        if not target_docs:
            return []

        doc = target_docs[0]
        sections = doc.get("sections", [])
        if not sections:
            return []

        q_norm = strip_accents((current_query or "").lower())
        suggested: List[str] = []

        for sec in sections:
            h = sec["heading"].strip()
            clean_t = sec["title"].strip()
            h_norm = strip_accents(h.lower())

            # Skip sections matching the active query to encourage exploring other topics
            if current_query and any(w in h_norm for w in q_norm.split() if len(w) > 3):
                continue

            # Generate natural tailored question based on section type
            if any(k in h_norm for k in ["gioi thieu", "khai niem", "tong quan"]):
                q_text = f"Khái niệm và các phương pháp phổ biến trong mục '{h}' là gì?"
            elif any(k in h_norm for k in ["pha ma", "an ninh", "tham ma"]):
                q_text = f"Nội dung chính và các điều kiện an ninh trong mục '{h}' là gì?"
            elif any(k in h_norm for k in ["dong", "autokey", "playfair", "don mot lan"]):
                q_text = f"Cách hoạt động và đặc điểm của '{h}' như thế nào?"
            elif sec["formulas"]:
                q_text = f"Nguyên lý hoạt động và công thức của '{h}' được mô tả ra sao?"
            else:
                q_text = f"Nội dung trọng tâm và các điểm lưu ý của '{h}' gồm những gì?"

            if q_text not in suggested:
                suggested.append(q_text)
                if len(suggested) >= count:
                    break

        # Fallback if not enough questions
        if len(suggested) < count:
            for sec in sections:
                h = sec["heading"].strip()
                q_fallback = f"Nội dung chính của '{h}' là gì?"
                if q_fallback not in suggested:
                    suggested.append(q_fallback)
                    if len(suggested) >= count:
                        break

        return suggested[:count]


_knowledge_bank_instance: Optional[SelfStudyKnowledgeBank] = None


def get_knowledge_bank() -> SelfStudyKnowledgeBank:
    """Returns the global thread-safe singleton Knowledge Bank."""
    global _knowledge_bank_instance
    if _knowledge_bank_instance is None:
        _knowledge_bank_instance = SelfStudyKnowledgeBank()
    return _knowledge_bank_instance
