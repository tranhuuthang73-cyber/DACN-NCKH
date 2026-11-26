"""
100% Local Self-Built Theoretical / Conceptual Practice & Multiple-Choice Quiz Generator.

ZERO external AI/LLM APIs.
Designed for non-formula / prose subjects (Philosophy / Triết học, Medicine / Y khoa,
History / Lịch sử, Law / Pháp luật, English / IELTS, Computer Networks, etc.).

Generates:
  - 3 grounded Multiple-Choice Questions (Câu 1, Câu 2, Câu 3) with options A, B, C, D
    and collapsible `- *Đáp án kiểm tra:* **Đáp án <X>** — <giải thích>` lines.
  - 1 Short-Answer / Conceptual Application Question (Câu 4) with `- *Đáp án kiểm tra:*`.
"""

from __future__ import annotations

import random
import re
import unicodedata
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple


def _strip_accents(text: str) -> str:
    if not text:
        return ""
    s = unicodedata.normalize("NFD", str(text))
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    return unicodedata.normalize("NFC", s).replace("đ", "d").replace("Đ", "D")


def _has_vietnamese_diacritics(text: str) -> bool:
    return any(ord(ch) > 127 and ch.isalpha() for ch in (text or ""))


_REQUEST_PHRASES: Tuple[str, ...] = (
    "cho tôi thêm",
    "cho mình thêm",
    "cho em thêm",
    "cho tôi",
    "cho mình",
    "cho em",
    "làm ơn",
    "vui lòng",
    "hãy giúp",
    "bài tập tự luyện",
    "bài tập luyện tập",
    "bài tập vận dụng",
    "bài tập trắc nghiệm",
    "câu hỏi trắc nghiệm",
    "câu hỏi ôn tập",
    "câu hỏi tự luyện",
    "ra đề bài tập",
    "ví dụ bài tập",
    "bài tập tương tự",
    "ví dụ tương tự",
    "trong tài liệu này",
    "trong tài liệu",
    "tài liệu này",
    "trong bài học này",
    "trong bài học",
    "trong bài này",
    "trong bài",
    "của bài học",
    "của bài",
    "bài học này",
    "bài này",
    "một số",
    "một vài",
    "bài tập",
    "ví dụ",
    "câu hỏi",
    "trắc nghiệm",
    "tự luận",
    "ôn tập",
    "tự luyện",
    "luyện tập",
    "ra đề",
    "thêm",
    "tạo",
    "sinh",
    "cho",
    "về",
    "phần",
    "mục",
    "chương",
    "chủ đề",
    "nội dung",
    "mới",
    "khác",
    "đi",
    "nhé",
    "nha",
    "với",
    "ạ",
    "hãy",
    "và",
    "hoặc",
    "hay",
    "cùng",
    "kèm",
    "theo",
    "từ",
    "thử",
)

_TOPIC_EDGE_STOPWORDS: Set[str] = {
    "cho", "toi", "minh", "em", "bai", "tap", "them", "tao", "sinh", "cau", "hoi",
    "trac", "nghiem", "on", "tu", "luyen", "ve", "phan", "muc", "chu", "de", "di",
    "nhe", "nha", "voi", "trong", "tai", "lieu", "nay", "do", "cac", "nhung", "mot",
    "vai", "so", "moi", "khac", "tuong", "giong", "vi", "du", "hay", "giup", "lam",
    "va", "hoac", "cung", "kem", "theo", "thu",
}

# Broken OCR pattern: isolated single Vietnamese consonant followed by space + lowercase fragment (e.g. `s ách`, `t riết`)
_BROKEN_OCR_RE = re.compile(
    r"(?<![A-Za-zÀ-ỹĐđ0-9_=/+\-])"
    r"\b[bcdfghjklmnpqrstvwxzđBCDFGHJKLMNPQRSTVWXZĐ]\s+"
    r"[a-záàảãạăắằẳẵặâấầẩẫậéèẻẽẹêếềểễệíìỉĩịóòỏõọôốồổỗộơớờởỡợúùủũụưứừửữựýỳỷỹỵđ]{2,}\b"
)

_RAW_HEADING_RE = re.compile(
    r"^(?:chương|phần|mục|bài|trang|page|slide|hình|bảng|table|figure)\s+[0-9ivxlcdm]+\b"
    r"|^\d+(?:\.\d+){1,4}\s+"
    r"|\.{4,}\s*\d+$",
    re.IGNORECASE,
)

_DEFINITIONAL_CUES: Tuple[str, ...] = (
    " là ", " bao gồm ", " đặc trưng ", " phản ánh ", " quyết định ",
    " đóng vai trò ", " biểu hiện ", " nguyên nhân ", " điều trị ", " chẩn đoán ",
    " được chia thành ", " dựa trên ", " khẳng định ", " xem xét ", " cho rằng ",
    " giúp ", " nhằm ", " có khả năng ", " refers to ", " is defined as ", " consists of ",
)


def extract_quiz_topic_focus(query: str) -> str:
    """
    Extracts explicit topic phrase from `query` after stripping exercise request words.
    Returns "" when the user asks a general exercise request (e.g. "cho tôi thêm bài tập đi").
    """
    cleaned = re.sub(r"\s+", " ", (query or "").strip())
    if not cleaned:
        return ""

    # Strip punctuation padding
    cleaned = cleaned.strip(" ?!.,;:\"'()[]{}")
    low = cleaned.lower()

    # Prefer explicit anchor after `về / phần / mục / chủ đề` when present
    anchor_m = re.search(
        r"\b(?:về\s+chủ\s+đề|về\s+phần|về\s+mục|chủ\s+đề|về|phần|mục)\s+(.+)$",
        low,
        flags=re.IGNORECASE,
    )
    if anchor_m:
        start_idx = anchor_m.start(1)
        candidate = cleaned[start_idx:].strip()
    else:
        candidate = cleaned
        for phrase in _REQUEST_PHRASES:
            candidate = re.sub(
                rf"(?<![A-Za-zÀ-ỹĐđ0-9]){re.escape(phrase)}(?![A-Za-zÀ-ỹĐđ0-9])",
                " ",
                candidate,
                flags=re.IGNORECASE,
            )

    # Trim trailing/leading filler words
    words = candidate.split()
    while words and _strip_accents(words[0].lower()).strip(".,;:!?") in _TOPIC_EDGE_STOPWORDS:
        words.pop(0)
    while words and _strip_accents(words[-1].lower()).strip(".,;:!?") in _TOPIC_EDGE_STOPWORDS:
        words.pop()

    topic = re.sub(r"\s+", " ", " ".join(words)).strip(" ?!.,;:\"'()[]{}-–")
    if len(_strip_accents(topic).replace(" ", "")) < 2:
        return ""
    return topic


def _whole_phrase_or_tokens_match(text: str, topic: str, accent_sensitive: bool) -> bool:
    if not text or not topic:
        return False
    hay = text.lower() if accent_sensitive else _strip_accents(text.lower())
    needle = topic.lower() if accent_sensitive else _strip_accents(topic.lower())
    needle = re.sub(r"\s+", " ", needle).strip()
    if not needle:
        return False

    phrase_pat = rf"(?<![a-zà-ỹđ0-9]){re.escape(needle)}(?![a-zà-ỹđ0-9])"
    if re.search(phrase_pat, hay):
        return True

    toks = [
        t for t in re.findall(r"[a-zà-ỹđ0-9]+", needle)
        if len(t) >= 2 and _strip_accents(t) not in _TOPIC_EDGE_STOPWORDS
    ]
    if not toks:
        return False

    matched = sum(
        1 for t in toks
        if re.search(rf"(?<![a-zà-ỹđ0-9]){re.escape(t)}(?![a-zà-ỹđ0-9])", hay)
    )
    if len(toks) <= 2:
        return matched == len(toks)
    return matched >= max(2, int(len(toks) * 0.75))


def _clean_sentence_text(raw: str) -> str:
    s = re.sub(r"\s+", " ", raw or "").strip()
    s = re.sub(r"^(?:[-•*▪◦+]|\d+[.)]|[a-zA-Z][.)])\s+", "", s).strip()
    s = re.sub(r"\[\d+\]", "", s).strip()
    return re.sub(r"\s{2,}", " ", s).strip()


def _is_clean_statement(sent: str) -> bool:
    if not sent:
        return False
    if sent.endswith(("?", ":")):
        return False
    if _RAW_HEADING_RE.search(sent):
        return False
    if _BROKEN_OCR_RE.search(sent):
        return False

    # Reject ALL-CAPS headings
    alpha_chars = [c for c in sent if c.isalpha()]
    if len(alpha_chars) < 18:
        return False
    upper_ratio = sum(1 for c in alpha_chars if c.isupper()) / float(len(alpha_chars))
    if upper_ratio > 0.55:
        return False

    words = sent.split()
    if not (10 <= len(words) <= 55):
        return False
    return True


def _extract_candidate_statements(
    paragraphs: Sequence[str],
    topic_focus: str = "",
) -> List[str]:
    candidates: List[Tuple[float, str]] = []
    seen_sigs: List[Set[str]] = []

    for para in paragraphs:
        p_norm = re.sub(r"\s*\n\s*", " ", para or "").strip()
        if not p_norm:
            continue
        raw_sents = re.split(r"(?<=[.!?])\s+(?=[A-ZÀ-ỸĐ0-9\"“])", p_norm)
        for rs in raw_sents:
            cleaned = _clean_sentence_text(rs)
            w_cnt = len(cleaned.split())
            # If slightly over 55 words, split cleanly on semicolon or secondary clause
            if 55 < w_cnt <= 95 and ";" in cleaned:
                cleaned = _clean_sentence_text(cleaned.split(";", 1)[0]) + "."
            if not cleaned.endswith((".", "!")):
                cleaned = cleaned.rstrip(",;:") + "."

            if not _is_clean_statement(cleaned):
                continue

            tok_sig = {
                w for w in re.findall(r"[a-z0-9]+", _strip_accents(cleaned.lower()))
                if len(w) >= 3
            }
            if len(tok_sig) < 4:
                continue
            if any(
                len(tok_sig & prev) / float(max(1, len(tok_sig | prev))) >= 0.65
                for prev in seen_sigs
            ):
                continue
            seen_sigs.append(tok_sig)

            score = 1.0
            low_s = f" {cleaned.lower()} "
            if any(cue in low_s for cue in _DEFINITIONAL_CUES):
                score += 2.0
            if topic_focus:
                if _whole_phrase_or_tokens_match(cleaned, topic_focus, accent_sensitive=True):
                    score += 3.5
                elif _whole_phrase_or_tokens_match(cleaned, topic_focus, accent_sensitive=False):
                    score += 2.5
            # Prefer crisp 14..38 word statements
            wc = len(cleaned.split())
            if 14 <= wc <= 38:
                score += 0.8
            candidates.append((score, cleaned))

    candidates.sort(key=lambda item: item[0], reverse=True)
    return [s for _, s in candidates]


_PERTURBATION_SWAPS: Tuple[Tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bquyết\s+định\b", re.IGNORECASE), "hoàn toàn phụ thuộc thụ động và không tác động gì đến"),
    (re.compile(r"\bcó\s+trước\b", re.IGNORECASE), "chỉ xuất hiện sau và bị quy định tuyệt đối bởi"),
    (re.compile(r"\bvận\s+động\s+và\s+phát\s+triển\b", re.IGNORECASE), "đứng im tuyệt đối, bất biến và tách rời mọi mối liên hệ"),
    (re.compile(r"\bmối\s+liên\s+hệ\s+phổ\s+biến\b", re.IGNORECASE), "trạng thái cô lập tuyệt đối, không liên quan lẫn nhau"),
    (re.compile(r"\bcô\s+lập,\s*tĩnh\s+tại\b", re.IGNORECASE), "vận động biến đổi không ngừng theo khuynh hướng đi lên"),
    (re.compile(r"\bbao\s+gồm\b", re.IGNORECASE), "loại trừ hoàn toàn và không bao giờ chứa"),
    (re.compile(r"\bgiúp\b", re.IGNORECASE), "ngăn cản hoàn toàn và làm mất khả năng"),
    (re.compile(r"\bđóng\s+vai\s+trò\b", re.IGNORECASE), "không có bất kỳ vai trò hay ảnh hưởng nào trong"),
    (re.compile(r"\blà\s+nguyên\s+nhân\b", re.IGNORECASE), "hoàn toàn không liên quan đến nguyên nhân"),
    (re.compile(r"\bcần\s+phải\b", re.IGNORECASE), "tuyệt đối không được phép"),
    (re.compile(r"\btăng\b", re.IGNORECASE), "giảm bằng không và triệt tiêu hoàn toàn"),
    (re.compile(r"\blà\b", re.IGNORECASE), "hoàn toàn không phải là"),
    (re.compile(r"\bis\s+defined\s+as\b", re.IGNORECASE), "is strictly unrelated to and excludes"),
    (re.compile(r"\brefers\s+to\b", re.IGNORECASE), "never involves or applies to"),
    (re.compile(r"\bis\b", re.IGNORECASE), "is never"),
)


def _falsify_statement(stmt: str, alt_subject: Optional[str] = None) -> str:
    """
    Produces a plausible, grammatically clean FALSE distractor grounded solely in
    the document's own terminology (never inventing formulas or external domains).
    """
    # If we have a contrasting subject from another concept in the same document, swap subject
    if alt_subject:
        m_cop = re.match(
            r"^([^,.;:!?]{3,55}?)\s+(là|bao gồm|đặc trưng bởi|khẳng định|xem xét|phản ánh)\s+(.+)$",
            stmt,
            flags=re.IGNORECASE,
        )
        if m_cop and _strip_accents(m_cop.group(1).lower()) != _strip_accents(alt_subject.lower()):
            return f"{alt_subject} {m_cop.group(2)} {m_cop.group(3)}"

    for pat, repl in _PERTURBATION_SWAPS:
        if pat.search(stmt):
            modified = pat.sub(repl, stmt, count=1)
            if modified != stmt:
                return modified

    # Safe fallback scope inversion without adding external facts
    trimmed = stmt.rstrip(".")
    return f"Mọi trường hợp đều phủ nhận hoàn toàn việc {trimmed[0].lower() + trimmed[1:]}."


def _extract_subject_terms(statements: Sequence[str]) -> List[str]:
    terms: List[str] = []
    seen: Set[str] = set()
    for st in statements:
        m = re.match(
            r"^([A-ZÀ-ỸĐ][^,.;:!?()]{2,50}?)\s+(?:là|bao gồm|được|khẳng định|xem xét|phản ánh|có)\b",
            st,
        )
        if m:
            cand = m.group(1).strip()
            norm = _strip_accents(cand.lower())
            if 2 <= len(norm.split()) <= 7 and norm not in seen:
                seen.add(norm)
                terms.append(cand)
    return terms


def _build_mcq_block(
    q_num: int,
    stem: str,
    correct_text: str,
    distractors: Sequence[str],
    explanation_quote: str,
    rng: random.Random,
    is_negative_stem: bool = False,
) -> str:
    labels = ["A", "B", "C", "D"]
    unique_dist: List[str] = []
    for d in distractors:
        d_clean = re.sub(r"\s+", " ", d).strip()
        if d_clean and d_clean != correct_text and d_clean not in unique_dist:
            unique_dist.append(d_clean)
        if len(unique_dist) == 3:
            break

    # Pad if short document yielded fewer than 3 distinct distractors
    pad_prefixes = (
        "Tài liệu bác bỏ nhận định này và khẳng định hoàn toàn ngược lại: ",
        "Phát biểu thu hẹp sai lệch phạm vi khi cho rằng chỉ duy nhất một yếu tố biệt lập chi phối mà không có ",
        "Nhận định gán ghép sai bản chất khi phủ nhận hoàn toàn nội dung: ",
    )
    pad_idx = 0
    while len(unique_dist) < 3:
        base = correct_text.rstrip(".")
        alt = _falsify_statement(base) if pad_idx == 0 else (
            f"{pad_prefixes[pad_idx % len(pad_prefixes)]}{base[:90].lower()}."
        )
        if alt not in unique_dist and alt != correct_text:
            unique_dist.append(alt)
        pad_idx += 1

    options_pool = [(True, correct_text)] + [(False, d) for d in unique_dist[:3]]
    rng.shuffle(options_pool)

    correct_letter = "A"
    option_lines: List[str] = []
    for idx, (is_ans, opt_txt) in enumerate(options_pool):
        letter = labels[idx]
        if is_ans:
            correct_letter = letter
        option_lines.append(f"{letter}. {opt_txt}")

    clean_quote = re.sub(r"\s+", " ", explanation_quote).strip()
    if is_negative_stem:
        ans_line = (
            f"- *Đáp án kiểm tra:* **Đáp án {correct_letter}** — "
            f"Phát biểu {correct_letter} không đúng với bài học; theo tài liệu: \"{clean_quote}\""
        )
    else:
        ans_line = (
            f"- *Đáp án kiểm tra:* **Đáp án {correct_letter}** — "
            f"Theo nội dung tài liệu: \"{clean_quote}\""
        )

    return f"**Câu {q_num}.** {stem}\n" + "\n".join(option_lines) + "\n" + ans_line


def generate_conceptual_practice(
    query: str,
    doc_text: str,
    doc_title: str = "Tài liệu",
    passages: Optional[Sequence[Any]] = None,
    seed: int = 42,
) -> Optional[Dict[str, Any]]:
    """
    Generates 3 grounded Multiple-Choice Questions + 1 Short-Answer Question
    purely from the uploaded document's prose concepts/statements.
    Returns None if an explicit topic focus does not appear anywhere in the document.
    """
    raw_paragraphs: List[str] = []
    if passages:
        for p in passages:
            txt = (
                p.get("text") or p.get("content") or p.get("snippet")
                if isinstance(p, dict)
                else getattr(p, "text", None) or getattr(p, "content", None)
            )
            if txt and str(txt).strip():
                raw_paragraphs.extend(
                    c.strip() for c in re.split(r"\n\s*\n+", str(txt)) if c.strip()
                )
    if doc_text and doc_text.strip():
        doc_paras = [c.strip() for c in re.split(r"\n\s*\n+", doc_text) if c.strip()]
        if not raw_paragraphs:
            raw_paragraphs = doc_paras
        elif len(raw_paragraphs) < 4:
            raw_paragraphs.extend(doc_paras)

    if not raw_paragraphs:
        return None

    topic_focus = extract_quiz_topic_focus(query)
    all_doc_statements = _extract_candidate_statements(raw_paragraphs, topic_focus="")

    if topic_focus:
        # Step 1: Accent-sensitive match
        matched_paras = [
            p for p in raw_paragraphs
            if _whole_phrase_or_tokens_match(p, topic_focus, accent_sensitive=True)
        ]
        # Step 2: Accent-insensitive fallback ONLY when user typed unaccented or doc lacks accents
        if not matched_paras and (
            not _has_vietnamese_diacritics(topic_focus)
            or not _has_vietnamese_diacritics(doc_text or " ".join(raw_paragraphs[:5]))
        ):
            matched_paras = [
                p for p in raw_paragraphs
                if _whole_phrase_or_tokens_match(p, topic_focus, accent_sensitive=False)
            ]

        if not matched_paras:
            return None

        focus_statements = _extract_candidate_statements(matched_paras, topic_focus=topic_focus)
        if not focus_statements:
            # Fallback within matched paragraphs for compact clean lines (7..65 words)
            for mp in matched_paras:
                for rs in re.split(r"(?<=[.!?])\s+|\n+", mp):
                    cs = _clean_sentence_text(rs)
                    if not cs.endswith("."):
                        cs = cs.rstrip(",;:") + "."
                    if 7 <= len(cs.split()) <= 65 and not _BROKEN_OCR_RE.search(cs):
                        focus_statements.append(cs)
            if not focus_statements:
                return None
        topic_label = topic_focus
    else:
        focus_statements = all_doc_statements
        if not focus_statements:
            return None
        subj_candidates = _extract_subject_terms(focus_statements[:6])
        topic_label = subj_candidates[0] if subj_candidates else (doc_title or "Nội dung trọng tâm")

    pool_all = list(dict.fromkeys(focus_statements + all_doc_statements))
    subjects = _extract_subject_terms(pool_all[:15])
    rng = random.Random(seed)

    s1 = focus_statements[0]
    s2 = focus_statements[1 % len(focus_statements)]
    s3 = focus_statements[2 % len(focus_statements)]

    other_pool = [s for s in pool_all if s not in {s1, s2, s3}]
    falsified_pool: List[str] = []
    for idx, src_s in enumerate((other_pool + focus_statements)[:8]):
        alt_subj = subjects[(idx + 1) % len(subjects)] if len(subjects) >= 2 else None
        falsified_pool.append(_falsify_statement(src_s, alt_subject=alt_subj))

    # Question 1: Identify accurate statement about topic
    q1_block = _build_mcq_block(
        q_num=1,
        stem=(
            f"Theo nội dung tài liệu **{doc_title}**, nhận định nào sau đây phản ánh **đúng** "
            f"về **{topic_label}**?"
        ),
        correct_text=s1,
        distractors=falsified_pool[:3],
        explanation_quote=s1,
        rng=rng,
        is_negative_stem=False,
    )

    # Question 2: Negative stem ("KHÔNG đúng") when >= 3 distinct true statements exist, else positive
    distinct_true = list(dict.fromkeys(focus_statements + other_pool))
    if len(distinct_true) >= 3:
        false_target = _falsify_statement(s2, alt_subject=subjects[-1] if len(subjects) >= 2 else None)
        true_distractors = [st for st in distinct_true if st != s2][:2] + [s1 if s1 != s2 else distinct_true[-1]]
        true_distractors = list(dict.fromkeys(true_distractors))[:3]
        q2_block = _build_mcq_block(
            q_num=2,
            stem=(
                f"Dựa trên kiến thức trong **{doc_title}**, phát biểu nào sau đây **KHÔNG đúng** "
                f"khi bàn về **{topic_label}** và các nội dung liên quan?"
            ),
            correct_text=false_target,
            distractors=true_distractors,
            explanation_quote=s2,
            rng=rng,
            is_negative_stem=True,
        )
    else:
        q2_block = _build_mcq_block(
            q_num=2,
            stem=f"Theo **{doc_title}**, điểm cốt lõi nào dưới đây được xác nhận trong bài học?",
            correct_text=s2,
            distractors=[_falsify_statement(s2)] + falsified_pool[1:3],
            explanation_quote=s2,
            rng=rng,
            is_negative_stem=False,
        )

    # Question 3: Conceptual detail / mechanism / implication from s3
    q3_distractors = [_falsify_statement(s3)] + falsified_pool[2:5]
    q3_block = _build_mcq_block(
        q_num=3,
        stem=(
            f"Khi phân tích sâu hơn về **{topic_label}** trong **{doc_title}**, "
            f"luận điểm nào sau đây là **chính xác**?"
        ),
        correct_text=s3,
        distractors=q3_distractors,
        explanation_quote=s3,
        rng=rng,
        is_negative_stem=False,
    )

    # Question 4: Short-answer / synthesis question
    key_points = list(dict.fromkeys([s1, s2, s3]))[:2]
    key_summary = " | ".join(re.sub(r"\s+", " ", kp).strip() for kp in key_points)
    q4_block = (
        f"**Câu 4 (Tự luận / Vận dụng ngắn).** Dựa vào tài liệu **{doc_title}**, "
        f"hãy trình bày khái quát bản chất / luận điểm trọng tâm về **{topic_label}** "
        f"và nêu điểm cần lưu ý khi phân tích hoặc vận dụng.\n"
        f"- *Đáp án kiểm tra:* Ý cốt lõi trong bài: {key_summary}"
    )

    header = (
        f"### 📝 Bài tập Trắc nghiệm & Tự luận Ôn tập: {topic_label}\n"
        f"*Bộ câu hỏi được trích lập trực tiếp từ nội dung lý thuyết của **{doc_title}** "
        f"(bấm vào từng mục đáp án để đối chiếu):*"
    )
    formatted_markdown = "\n\n".join([header, q1_block, q2_block, q3_block, q4_block])

    return {
        "answer": formatted_markdown,
        "questions_generated": 4,
        "engine": "ConceptualQuizGenerator-SelfBuilt",
        "topic_matched": topic_label,
    }


__all__ = [
    "extract_quiz_topic_focus",
    "generate_conceptual_practice",
]
