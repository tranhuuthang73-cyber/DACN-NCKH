"""
Self-Built Pedagogical Schema Synthesizer & Auto-Thinking Selector.

100% Local Offline, Zero External API, Zero LLM Weights.
Provides:
  1. `resolve_auto_thinking_mode` & `should_auto_promote_fast_query`:
     Deterministic complexity-aware routing across `fast`, `deep`, and `broad`.
  2. `build_comparison_markdown_table`:
     Strictly grounded GitHub-Flavored Markdown comparison table extracted
     exclusively from source evidence sentences (zero invented words).
  3. `build_step_flow_markdown`:
     Grounded step-by-step process/mechanism flow formatter (`Bước 1..5`).
"""

from __future__ import annotations

import re
import unicodedata
from typing import List, Optional, Sequence, Set, Tuple

from src.brain.grounded_explainer import (
    _jaccard_and_containment,
    _trim_words,
    compress_clause,
    extract_frame,
)
from src.brain.neural_discourse_scorer import _detect_heading_or_marker
from src.brain.textrank_salience import strip_accents


# ---------------------------------------------------------------------------
# 1. Auto-Thinking Mode Selector
# ---------------------------------------------------------------------------

_COMPARISON_FOLDED_RE = re.compile(
    r"\b(?:so\s+sanh|phan\s+biet|khac\s+nhau|diem\s+khac|khac\s+gi|"
    r"compare|comparison|versus|vs\.?)\b",
    re.IGNORECASE,
)

_WHY_STRICT_FOLDED_RE = re.compile(
    r"\b(?:tai\s+sao|vi\s+sao|why\s+(?:does|do|is|are|did|can|should))\b",
    re.IGNORECASE,
)

_CAUSAL_AUTO_FOLDED_RE = re.compile(
    r"\b(?:tai\s+sao|vi\s+sao|nguyen\s+nhan|ban\s+chat|why)\b",
    re.IGNORECASE,
)

_MULTI_DOC_COMPARISON_FOLDED_RE = re.compile(
    r"\b(?:giua\s+cac\s+tai\s+lieu|trong\s+cac\s+tai\s+lieu|"
    r"across\s+documents|between\s+documents)\b",
    re.IGNORECASE,
)

_FULL_DOC_SUMMARY_FOLDED_RE = re.compile(
    r"\b(?:tom\s+tat\s+toan\s+bo|tong\s+quan\s+tai\s+lieu|"
    r"tom\s+tat\s+ca\s+tai\s+lieu|tom\s+tat\s+toan\s+van|"
    r"tong\s+quan\s+toan\s+bo|khai\s+quat\s+toan\s+bo|"
    r"full\s+document\s+summary|summarize\s+the\s+(?:entire|whole)\s+document)\b",
    re.IGNORECASE,
)

# Compound nouns containing "tính" that are NOT math calculation requests
_NON_MATH_TINH_COMPOUNDS_RE = re.compile(
    r"\b(?:máy\s+tính|thuộc\s+tính|đặc\s+tính|tính\s+chất|tính\s+năng|"
    r"tuyến\s+tính|giới\s+tính|tính\s+từ|tính\s+khả\s+thi|tính\s+bảo\s+mật|"
    r"tính\s+toàn\s+vẹn|tính\s+nhất\s+quán|tính\s+sẵn\s+sàng|tính\s+chính\s+xác|"
    r"tính\s+ổn\s+định|tính\s+đúng\s+đắn|cá\s+tính|bản\s+tính)\b",
    re.IGNORECASE,
)

_MATH_EXERCISE_FOLDED_RE = re.compile(
    r"\b(?:cong\s+thuc|bai\s+tap|chung\s+minh|tinh\s+toan|cach\s+tinh|"
    r"giai\s+phuong\s+trinh|formula|prove|calculate|compute)\b",
    re.IGNORECASE,
)

_CROSS_SYNTHESIS_FOLDED_RE = re.compile(
    r"\b(?:ket\s+hop\s+cac\s+doan|tong\s+hop\s+tu\s+nhieu|lien\s+he\s+giua)\b",
    re.IGNORECASE,
)


def _has_math_or_exercise_cue(q_nfc: str, q_folded: str) -> bool:
    if _MATH_EXERCISE_FOLDED_RE.search(q_folded):
        return True
    scrubbed = _NON_MATH_TINH_COMPOUNDS_RE.sub(" ", q_nfc.lower())
    return bool(re.search(r"(?<!\w)tính(?!\w)", scrubbed, flags=re.UNICODE))


def should_auto_promote_fast_query(query: str, route_value: str = "") -> Optional[str]:
    """
    Returns `"deep"` ONLY on high-complexity analytical queries
    (comparison, `tại sao`/`vì sao`, multi-document comparison) and `None` otherwise.
    """
    q_raw = unicodedata.normalize("NFC", (query or "").strip())
    r_up = (route_value or "").strip().upper()
    if r_up == "CROSS_DOCUMENT_COMPARISON":
        return "deep"
    if not q_raw:
        return None

    q_folded = strip_accents(q_raw.lower())
    if (
        _COMPARISON_FOLDED_RE.search(q_folded)
        or _WHY_STRICT_FOLDED_RE.search(q_folded)
        or _MULTI_DOC_COMPARISON_FOLDED_RE.search(q_folded)
    ):
        return "deep"
    return None


def resolve_auto_thinking_mode(
    query: str,
    route_value: str = "",
    requested_mode: str = "fast",
) -> Tuple[str, bool]:
    """
    Resolves effective thinking mode and reports whether auto-promotion occurred.

    - Explicit `"deep"`, `"broad"`, or `"deep_broad"` -> `(requested_mode, False)`.
    - `"auto"` -> promotes to `"deep"` on comparison, causal/why, multi-part (` và `
      with >= 8 words), math/formulas/exercises, or cross-doc/multi-passage synthesis;
      promotes to `"broad"` on full-document summary; otherwise `"fast"`.
      Returns `(resolved_mode, resolved_mode != "fast")`.
    - Any other mode (including `"fast"`) -> `("fast", False)`.
    """
    req = (requested_mode or "fast").strip().lower()
    if req in ("deep", "broad", "deep_broad"):
        return req, False
    if req != "auto":
        return "fast", False

    q_nfc = unicodedata.normalize("NFC", (query or "").strip())
    q_low = q_nfc.lower()
    q_folded = strip_accents(q_low)
    r_up = (route_value or "").strip().upper()
    word_count = len(q_nfc.split())

    is_comp_or_causal_or_math = (
        r_up == "CROSS_DOCUMENT_COMPARISON"
        or bool(_COMPARISON_FOLDED_RE.search(q_folded))
        or bool(_MULTI_DOC_COMPARISON_FOLDED_RE.search(q_folded))
        or bool(_CAUSAL_AUTO_FOLDED_RE.search(q_folded))
        or _has_math_or_exercise_cue(q_nfc, q_folded)
    )
    is_full_summary = bool(_FULL_DOC_SUMMARY_FOLDED_RE.search(q_folded))

    if is_full_summary and not is_comp_or_causal_or_math:
        return "broad", True

    is_multi_part = word_count >= 8 and (" và " in f" {q_low} " or " and " in f" {q_low} ")
    is_cross_synth = r_up in ("CROSS_DOCUMENT_COMPARISON", "MULTI_PASSAGE_SYNTHESIS") or bool(
        _CROSS_SYNTHESIS_FOLDED_RE.search(q_folded)
    )

    if is_comp_or_causal_or_math or is_cross_synth or is_multi_part:
        return "deep", True

    if is_full_summary or r_up == "DOCUMENT_SUMMARY":
        return "broad", True

    return "fast", False


# ---------------------------------------------------------------------------
# 2. Grounded Comparison Markdown Table Synthesizer
# ---------------------------------------------------------------------------

_CONTRAST_LEAD_RE = re.compile(
    r"^(?:"
    r"(?:ngược\s+lại\s+với|trái\s+ngược\s+với|trái\s+với|khác\s+với|đối\s+lập\s+với|"
    r"phân\s+biệt\s+với|so\s+với|unlike|in\s+contrast\s+to|contrary\s+to|compared\s+to|compared\s+with)"
    r"\s+[^,;:]{2,65},\s*"
    r"|(?:trong\s+khi\s+đó|trong\s+khi|ngược\s+lại|trái\s+lại|mặt\s+khác|"
    r"tuy\s+nhiên|bên\s+cạnh\s+đó|ngoài\s+ra|đối\s+với|về\s+phía|còn|"
    r"whereas|while|on\s+the\s+other\s+hand|in\s+contrast|conversely)[,:\s]+"
    r")",
    re.IGNORECASE,
)

_NON_ENTITY_SUBJECT_STARTS = {
    "trong", "khi", "neu", "vi", "boi", "do", "nho", "theo", "tai", "tu",
    "de", "qua", "thong", "tren", "duoi", "ngoai", "ben", "tuy", "mac",
    "no", "ho", "chung", "dieu", "viec", "phan", "muc", "chuong", "trang",
    "tai lieu", "bai viet", "ket qua", "phuong phap nay", "he thong nay",
    "mo hinh nay", "this", "these", "those", "it", "they", "there", "when", "if",
}

_QUERY_PAIR_PATTERNS: Tuple[re.Pattern, ...] = (
    re.compile(
        r"(?:so\s+sánh|phân\s+biệt|điểm\s+khác\s+nhau\s+giữa|khác\s+nhau\s+giữa|compare)\s+"
        r"(?:giữa\s+)?(.{1,45}?)\s+(?:và|với|vs\.?|versus|and)\s+(.{1,45}?)"
        r"(?:\s+(?:khác\s+nhau|giống\s+nhau|khác\s+gì|trong|ở|về|như\s+thế\s+nào|ra\s+sao|là\s+gì).*)?(?:\s*[?.!]|$)",
        re.IGNORECASE,
    ),
    re.compile(
        r"^(.{1,40}?)\s+(?:vs\.?|versus|khác\s+gì(?:\s+với)?)\s+(.{1,40}?)(?:\s*[?.!]|$)",
        re.IGNORECASE,
    ),
)

_TRAILING_ENTITY_NOISE_RE = re.compile(
    r"\s+(?:khác\s+nhau(?:\s+như\s+thế\s+nào|\s+ra\s+sao|\s+ở\s+điểm\s+nào)?|"
    r"giống\s+nhau.*|như\s+thế\s+nào.*|ra\s+sao.*|ở\s+điểm\s+nào.*|trong\s+tài\s+liệu.*)$",
    re.IGNORECASE,
)


def _clean_entity_label(raw: str) -> str:
    txt = unicodedata.normalize("NFC", (raw or "").strip())
    txt = re.sub(r"[*_`\"'“”‘’]+", "", txt)
    txt = _CONTRAST_LEAD_RE.sub("", txt).strip(" ,;:.!?-–—()[]{}")
    txt = _TRAILING_ENTITY_NOISE_RE.sub("", txt).strip(" ,;:.!?-–—()[]{}")
    txt = re.sub(r"\s{2,}", " ", txt).strip()
    return txt


def _is_valid_entity_name(name: str) -> bool:
    if not name:
        return False
    words = name.split()
    if not (1 <= len(words) <= 7) or len(name) > 60:
        return False
    folded = strip_accents(name.lower())
    first_tok = folded.split()[0]
    if first_tok in _NON_ENTITY_SUBJECT_STARTS or folded in _NON_ENTITY_SUBJECT_STARTS:
        return False
    if re.fullmatch(r"[\d\W_]+", name):
        return False
    return True


def _extract_entities_from_query_grounded(
    query: str,
    evidence_texts: Sequence[str],
) -> List[str]:
    q_nfc = unicodedata.normalize("NFC", (query or "").strip())
    if not q_nfc:
        return []
    joined_ev_low = unicodedata.normalize("NFC", " \n ".join(evidence_texts)).lower()
    for pat in _QUERY_PAIR_PATTERNS:
        m = pat.search(q_nfc)
        if not m:
            continue
        cand_a = _clean_entity_label(m.group(1))
        cand_b = _clean_entity_label(m.group(2))
        if (
            _is_valid_entity_name(cand_a)
            and _is_valid_entity_name(cand_b)
            and strip_accents(cand_a.lower()) != strip_accents(cand_b.lower())
            and cand_a.lower() in joined_ev_low
            and cand_b.lower() in joined_ev_low
        ):
            return [cand_a, cand_b]
    return []


_TRAILING_CIT_RE = re.compile(r"(?:\s*\[\d+\])+\s*$")


def _escape_md_cell(text: str) -> str:
    cleaned = re.sub(r"[\r\n]+", " ", text or "")
    cleaned = cleaned.replace("|", r"\|")
    return re.sub(r"\s{2,}", " ", cleaned).strip()


def _extract_verbatim_clause_for_entity(
    raw_sentence: str,
    entity_name: str,
    citation_label: str,
    max_words: int = 28,
) -> str:
    """
    Extracts a concise cell statement strictly from `raw_sentence` without
    inventing or substituting any word outside the source sentence.
    """
    s = unicodedata.normalize("NFC", (raw_sentence or "").strip())
    s = re.sub(r"\[?[A-Z0-9_\-]+::P\d+\]?", "", s)
    s = re.sub(r"^[-*•+–—]\s*", "", s).strip()
    s = _TRAILING_CIT_RE.sub("", s).strip(" .;")
    s = _CONTRAST_LEAD_RE.sub("", s).strip(" ,;:")

    # Strip leading entity repetition so cell focuses on predicate/role
    ent_clean = entity_name.strip()
    if ent_clean:
        ent_prefix_re = re.compile(
            rf"^{re.escape(ent_clean)}\s*(?::\s*|\s+)",
            re.IGNORECASE | re.UNICODE,
        )
        m_pref = ent_prefix_re.match(s)
        if m_pref and len(s[m_pref.end() :].split()) >= 3:
            s = s[m_pref.end() :].strip(" ,;:")

    cit = (citation_label or "[1]").strip()
    if not re.fullmatch(r"\[\d+\]", cit):
        m_c = re.search(r"\[\d+\]", cit)
        cit = m_c.group(0) if m_c else "[1]"

    budget = max(6, max_words - 1)
    trimmed = _trim_words(s, max_words=budget).strip(" .,;:")
    if not trimmed:
        return ""
    if trimmed[0].islower():
        trimmed = trimmed[0].upper() + trimmed[1:]

    cell = _escape_md_cell(f"{trimmed} {cit}")
    # Guarantee <= max_words
    cell_words = cell.split()
    if len(cell_words) > max_words:
        body_part = " ".join(cell_words[: max_words - 1]).rstrip(".,;:")
        cell = f"{body_part} {cit}"
    return cell


def _entity_matches_sentence(entity: str, subj: str, sentence: str) -> int:
    """Returns match strength: 2 = subject match, 1 = mention in sentence, 0 = no match."""
    ent_low = unicodedata.normalize("NFC", entity).lower()
    ent_fold = strip_accents(ent_low)
    subj_low = unicodedata.normalize("NFC", subj).lower()
    subj_fold = strip_accents(subj_low)
    sent_low = unicodedata.normalize("NFC", sentence).lower()

    if subj_low and (ent_low == subj_low or ent_fold == subj_fold or ent_low in subj_low):
        return 2
    if re.search(rf"(?<!\w){re.escape(ent_low)}(?!\w)", sent_low, flags=re.UNICODE):
        return 1
    return 0


def build_comparison_markdown_table(
    query: str,
    evidence_items: Sequence[Tuple[str, str]],
    entity_names: Optional[Sequence[str]] = None,
) -> Optional[str]:
    """
    Synthesizes a clean GitHub-Flavored Markdown comparison table strictly from
    `evidence_items` (`(sentence_text, citation_label)` pairs, >= 2 items),
    without inventing any word outside the evidence.

    Returns `None` if two distinct short entity names (<= 7 words each) and
    corresponding grounded statements cannot be cleanly extracted.
    """
    if not evidence_items or len(evidence_items) < 2:
        return None

    valid_items: List[Tuple[str, str]] = []
    for item in evidence_items:
        if not item or len(item) < 2:
            continue
        sent_txt = unicodedata.normalize("NFC", str(item[0] or "").strip())
        cit_lbl = str(item[1] or "[1]").strip() or "[1]"
        if sent_txt and not _detect_heading_or_marker(sent_txt):
            valid_items.append((sent_txt, cit_lbl))

    if len(valid_items) < 2:
        return None

    # Pre-extract frames on contrast-stripped sentences to discover true grammatical subjects
    extracted_subjects: List[str] = []
    for sent_txt, cit_lbl in valid_items:
        stripped_for_subj = _CONTRAST_LEAD_RE.sub("", sent_txt).strip()
        fr = extract_frame(
            stripped_for_subj,
            role="COMPARISON_CONTRAST",
            salience=1.0,
            citation_label=cit_lbl,
        )
        core_cmp = fr.compressed_text.rstrip(".!? ").strip()
        # Only accept subject when extract_frame found a real subject/predicate split
        if fr.predicate.strip() != core_cmp.strip():
            cand_s = _clean_entity_label(fr.subject)
            if _is_valid_entity_name(cand_s):
                extracted_subjects.append(cand_s)
            else:
                extracted_subjects.append("")
        else:
            extracted_subjects.append("")

    chosen_entities: List[str] = []
    seen_ent_fold: Set[str] = set()

    if entity_names and len(entity_names) >= 2:
        for raw_e in entity_names:
            ce = _clean_entity_label(raw_e)
            ef = strip_accents(ce.lower())
            if _is_valid_entity_name(ce) and ef not in seen_ent_fold:
                seen_ent_fold.add(ef)
                chosen_entities.append(ce)
                if len(chosen_entities) == 2:
                    break

    if len(chosen_entities) < 2:
        chosen_entities.clear()
        seen_ent_fold.clear()
        for cand_s in extracted_subjects:
            if not cand_s:
                continue
            ef = strip_accents(cand_s.lower())
            if ef not in seen_ent_fold:
                seen_ent_fold.add(ef)
                chosen_entities.append(cand_s)
                if len(chosen_entities) == 2:
                    break

    if len(chosen_entities) < 2:
        q_ents = _extract_entities_from_query_grounded(
            query, [s for s, _ in valid_items]
        )
        if len(q_ents) == 2:
            chosen_entities = q_ents

    if len(chosen_entities) < 2:
        return None

    ent_a, ent_b = chosen_entities[0], chosen_entities[1]

    bucket_a: List[Tuple[str, str]] = []
    bucket_b: List[Tuple[str, str]] = []

    for idx, (sent_txt, cit_lbl) in enumerate(valid_items):
        subj_i = extracted_subjects[idx]
        core_sent_txt = _CONTRAST_LEAD_RE.sub("", sent_txt).strip() or sent_txt
        score_a = _entity_matches_sentence(ent_a, subj_i, core_sent_txt)
        score_b = _entity_matches_sentence(ent_b, subj_i, core_sent_txt)

        if score_a > score_b and score_a > 0:
            bucket_a.append((sent_txt, cit_lbl))
        elif score_b > score_a and score_b > 0:
            bucket_b.append((sent_txt, cit_lbl))
        elif score_a > 0 and score_b > 0:
            # Compound contrast sentence mentioning both entities -> split on contrast connector if present
            m_split = re.search(
                r"(?:;\s*|\s*,\s*)(?:trong\s+khi(?:\s+đó)?|còn|ngược\s+lại|mặt\s+khác|whereas|while)\s+",
                sent_txt,
                flags=re.IGNORECASE,
            )
            if m_split:
                left_s = sent_txt[: m_split.start()].strip()
                right_s = sent_txt[m_split.end() :].strip()
                if _entity_matches_sentence(ent_a, "", left_s) >= _entity_matches_sentence(ent_b, "", left_s):
                    bucket_a.append((left_s, cit_lbl))
                    bucket_b.append((right_s, cit_lbl))
                else:
                    bucket_b.append((left_s, cit_lbl))
                    bucket_a.append((right_s, cit_lbl))

    if not bucket_a or not bucket_b:
        return None

    core_a = _extract_verbatim_clause_for_entity(bucket_a[0][0], ent_a, bucket_a[0][1], max_words=28)
    core_b = _extract_verbatim_clause_for_entity(bucket_b[0][0], ent_b, bucket_b[0][1], max_words=28)
    if not core_a or not core_b:
        return None

    head_a = _escape_md_cell(ent_a)
    head_b = _escape_md_cell(ent_b)

    is_def_pair = all(
        re.match(r"^(?:Là|Được\s+định\s+nghĩa|Được\s+hiểu|Is|Refers)\b", c, re.IGNORECASE)
        for c in (core_a, core_b)
    )
    row1_label = "**Bản chất / Định nghĩa**" if is_def_pair else "**Bản chất / Vai trò**"

    rows: List[str] = [
        f"| Tiêu chí | {head_a} | {head_b} |",
        "| :--- | :--- | :--- |",
        f"| {row1_label} | {core_a} | {core_b} |",
    ]

    # Optional Row 2 (Đặc điểm / Cơ chế) when both entities have distinct secondary evidence
    if len(bucket_a) >= 2 and len(bucket_b) >= 2:
        mech_a = _extract_verbatim_clause_for_entity(bucket_a[1][0], ent_a, bucket_a[1][1], max_words=28)
        mech_b = _extract_verbatim_clause_for_entity(bucket_b[1][0], ent_b, bucket_b[1][1], max_words=28)
        jacc_a, _ = _jaccard_and_containment(bucket_a[0][0], bucket_a[1][0])
        jacc_b, _ = _jaccard_and_containment(bucket_b[0][0], bucket_b[1][0])
        if mech_a and mech_b and jacc_a < 0.70 and jacc_b < 0.70:
            rows.append(f"| **Đặc điểm / Cơ chế** | {mech_a} | {mech_b} |")

    return "\n".join(rows)


# ---------------------------------------------------------------------------
# 3. Grounded Step-by-Step Pedagogical Flow Formatter
# ---------------------------------------------------------------------------

_STEP_FLOW_TRIGGER_FOLDED_RE = re.compile(
    r"(?:\bquy\s+trinh\b|\bcac\s+buoc\b|\btung\s+buoc\b|\btrinh\s+tu\b|"
    r"\bhoat\s+dong\s+nhu\s+the\s+nao\b|\bhoat\s+dong\s+ra\s+sao\b|"
    r"\bvan\s+hanh\s+nhu\s+the\s+nao\b|\bcach\s+thuc\s+hien\b|"
    r"\bcach\s+hoat\s+dong\b|\bdien\s+ra\s+nhu\s+the\s+nao\b|"
    r"\bdien\s+ra\s+ra\s+sao\b|\bstep[\s-]+by[\s-]+step\b|\bworkflow\b|"
    r"\bhow\s+does\s+.{2,50}\s+work\b)",
    re.IGNORECASE,
)

_EXISTING_STEP_PREFIX_RE = re.compile(
    r"^(?:[-*•+–—]\s*)?(?:(?:bước|step|giai\s+đoạn)\s*\d+\s*[:.\-–—)]\s*|\d+\s*[.)]\s+)",
    re.IGNORECASE,
)


def build_step_flow_markdown(
    query: str,
    sentences_with_cits: Sequence[Tuple[str, str]],
) -> Optional[str]:
    """
    Formats grounded `(sentence, citation_label)` pairs into a clean 2..5 step
    pedagogical flow when `query` asks about a process, workflow, steps, or mechanism.
    """
    if not sentences_with_cits or len(sentences_with_cits) < 2:
        return None

    q_folded = strip_accents((query or "").strip().lower())
    if not q_folded or not _STEP_FLOW_TRIGGER_FOLDED_RE.search(q_folded):
        return None

    deduped_steps: List[Tuple[str, str]] = []
    seen_texts: List[str] = []

    for item in sentences_with_cits:
        if not item or len(item) < 2:
            continue
        raw_sent = unicodedata.normalize("NFC", str(item[0] or "").strip())
        cit_lbl = str(item[1] or "[1]").strip() or "[1]"
        if not raw_sent or _detect_heading_or_marker(raw_sent):
            continue

        cleaned_in = _TRAILING_CIT_RE.sub("", raw_sent).strip()
        cleaned_in = _EXISTING_STEP_PREFIX_RE.sub("", cleaned_in).strip()
        comp = compress_clause(cleaned_in)
        comp = _TRAILING_CIT_RE.sub("", comp).strip()
        if not comp or len(comp.split()) < 3:
            continue

        is_dup = False
        for prev in seen_texts:
            if strip_accents(comp.lower()) == strip_accents(prev.lower()):
                is_dup = True
                break
            jacc, cont = _jaccard_and_containment(comp, prev)
            if jacc >= 0.65 or cont >= 0.82:
                is_dup = True
                break
        if is_dup:
            continue

        if not re.fullmatch(r"\[\d+\]", cit_lbl):
            m_c = re.search(r"\[\d+\]", cit_lbl)
            cit_lbl = m_c.group(0) if m_c else "[1]"

        seen_texts.append(comp)
        deduped_steps.append((comp, cit_lbl))
        if len(deduped_steps) >= 5:
            break

    if len(deduped_steps) < 2:
        return None

    lines = [
        f"- **Bước {idx}:** {clause} {cit}"
        for idx, (clause, cit) in enumerate(deduped_steps, start=1)
    ]
    return "\n".join(lines)


__all__ = [
    "resolve_auto_thinking_mode",
    "should_auto_promote_fast_query",
    "build_comparison_markdown_table",
    "build_step_flow_markdown",
]
