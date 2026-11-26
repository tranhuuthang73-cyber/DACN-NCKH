"""
Phase 5.2 — Chat Session Manager & Conversational Context Resolver.
Manages multi-turn conversation sessions, document attachments, and conversational memory.

STRICT RULE: NO TRAINING, NO GRADIENT UPDATES, FROZEN INFERENCE ONLY.
"""

import os
import re
import json
import time
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional, Sequence, Set, Tuple

NEED_CLARIFICATION = "NEED_CLARIFICATION"


def _extract_prior_constraints(query: str) -> str:
    """Extracts scope/condition constraints from a prior turn (Rule 3) so they remain attached."""
    if not query:
        return ""
    patterns = [
        r"\b(?:ở|trong|tại)\s+(?:phần|chương|mục|bài|trang|slide)\s+\d+(?:\.\d+)*\b",
        r"\b(?:ở|trong|với)\s+điều\s+kiện\s+[^,.;?!]{2,35}",
        r"\bvới\s+khóa\s+[^,.;?!]{1,25}",
    ]
    found: List[str] = []
    for pat in patterns:
        for m in re.finditer(pat, query, flags=re.IGNORECASE):
            val = m.group(0).strip(" ,.;?!")
            if val and not any(val.lower() in f.lower() for f in found):
                found.append(val)
    return ", ".join(found[:2])


def _extract_multi_entities_from_turn(query: str) -> List[str]:
    """Detects whether a prior user query asked about 2+ distinct parallel concepts/entities."""
    if not query:
        return []
    try:
        from src.web.document_analyzer import _extract_compound_concept_parts

        # Strip scope prepositions ("Trong chương 2, ...") before splitting on commas
        q_clean = query
        pc = _extract_prior_constraints(query)
        if pc:
            for item in pc.split(","):
                q_clean = re.sub(re.escape(item.strip()), "", q_clean, flags=re.IGNORECASE)
        q_clean = q_clean.strip(" ,;:-")
        parts = _extract_compound_concept_parts(q_clean)
        if len(parts) >= 2:
            generic = {
                "ưu điểm", "nhược điểm", "đặc điểm", "cơ chế", "vai trò",
                "nguyên lý", "mục tiêu", "phạm vi", "nội dung", "ý nghĩa",
            }
            if not any(p.strip().lower() in generic for p in parts):
                return parts[:5]
    except Exception:
        pass
    return []


def _has_document_self_reference(q_lower: str) -> bool:
    """Returns True when 'này'/'đó' refers to the attached document/section itself, not a missing chat turn."""
    return bool(
        re.search(
            r"\b(?:tài\s+liệu|văn\s+bản|bài\s+báo|bài\s+học|bài\s+giảng|file|giáo\s+trình|slide|chương|mục|phần|topic|chủ\s+đề)\s+(?:này|đó|\d+)\b",
            q_lower,
            flags=re.IGNORECASE,
        )
    )


def rewrite_standalone_query(
    conversation_history: Sequence[Dict[str, Any]],
    current_question: str,
    allow_clarification: bool = True,
) -> Tuple[str, Dict[str, Any]]:
    """
    Self-built conversational query rewriter (Rules 1-7, zero external LLM APIs).
    Returns (rewritten_query_or_NEED_CLARIFICATION, metadata_dict).
    """
    q_raw = re.sub(r"\s+", " ", (current_question or "").strip())
    if not q_raw:
        return "", {"status": "empty"}

    # Clean off copy-pasted numbering & category badge: e.g. "2. **[Chủ đề bài học]**: Query"
    clean_pasted = re.sub(r"^\s*\d+[\.\)]\s*(?:\*\*\[.*?\]\*\*:\s*|\[.*?\]:?\s*)?", "", q_raw).strip()
    if clean_pasted and clean_pasted != q_raw and len(clean_pasted.split()) >= 2:
        return clean_pasted, {"status": "normalized_pasted"}

    q_lower = q_raw.lower()
    history = list(conversation_history or [])
    # Exclude current_question if it was already appended as the trailing user message
    if history and history[-1].get("role") == "user" and (history[-1].get("content") or "").strip() == q_raw:
        prior_msgs = history[:-1]
    else:
        prior_msgs = history

    # 1. Check indexed references: "câu 2", "ý 2", "giải thích kỹ hơn ý thứ 2", "cho ví dụ về ý 1", "#2"
    # Note: "mục" is intentionally excluded so section queries like "cho biết mục 3" stay standalone!
    idx_match = re.search(
        r"^(?P<prefix>(?:trả\s+lời|hỏi|cho\s+biết|cho\s+ví\s+dụ(?:\s+về)?|ví\s+dụ(?:\s+về)?|"
        r"giải\s+thích(?:\s+kỹ(?:\s+hơn)?|\s+chi\s+tiết(?:\s+hơn)?|\s+rõ(?:\s+hơn)?)?(?:\s+về)?|"
        r"phân\s+tích(?:\s+kỹ(?:\s+hơn)?)?(?:\s+về)?|làm\s+rõ(?:\s+về)?|nêu(?:\s+rõ)?)\s+)?"
        r"(?P<kind>câu(?:\s*hỏi)?|ý|điểm|luận\s+điểm|bước|question)\s*(?:thứ\s*|số\s*)?(?P<num>\d+)\b(?P<tail>.*)$",
        q_raw,
        flags=re.IGNORECASE,
    )
    target_idx = -1
    kind_token = ""
    custom_prefix = ""
    custom_tail = ""
    if idx_match:
        kind_token = idx_match.group("kind").lower().strip()
        target_idx = int(idx_match.group("num")) - 1
        custom_prefix = (idx_match.group("prefix") or "").strip()
        custom_tail = (idx_match.group("tail") or "").strip(" ?:.,-")
    else:
        hash_match = re.match(r"^#?(\d+)\.?$", q_lower)
        if hash_match:
            kind_token = "câu"
            target_idx = int(hash_match.group(1)) - 1

    if target_idx >= 0:
        prefer_bullets = kind_token in ("ý", "điểm", "luận điểm", "bước")
        last_assistant = next(
            (
                m for m in reversed(prior_msgs)
                if m.get("role") == "assistant" and m.get("routing") != "CLARIFICATION_NEEDED"
            ),
            None,
        )
        if last_assistant is None:
            if allow_clarification:
                return NEED_CLARIFICATION, {"status": NEED_CLARIFICATION, "reason": "no_prior_assistant_turn"}
            return q_raw, {"status": "unchanged"}

        c_text = last_assistant.get("content", "")
        body_only = c_text.split("### Nguồn")[0].split("💡")[0]
        bullet_lines = re.findall(r"^\s*[-•]\s+(.+)$", body_only, re.MULTILINE)
        s_qs = list(last_assistant.get("suggested_questions") or [])
        if not s_qs:
            numbered_lines = re.findall(r"^\s*(\d+)\.\s*(.+)$", c_text, re.MULTILINE)
            s_qs = [item[1].strip() for item in numbered_lines]

        def _clean_facet(raw_f: str) -> str:
            f = re.sub(r"\[[^\]]+\]", "", raw_f)
            f = f.replace("**", "").strip()
            f = re.sub(r"^(?:Ý|Điểm|Bước|Luận\s+điểm)\s*\d+\s*[:.\-–]\s*", "", f, flags=re.IGNORECASE).strip()
            return f.rstrip(".")

        def _format_facet_query(facet: str) -> str:
            if custom_prefix and any(w in custom_prefix.lower() for w in ("ví dụ", "phân tích")):
                return f"{custom_prefix} {facet}" + (f" ({custom_tail})" if custom_tail else "")
            if custom_tail and len(custom_tail.split()) >= 2:
                return f"{facet} {custom_tail}?"
            return f"Giải thích chi tiết nội dung: {facet}"

        if prefer_bullets and 0 <= target_idx < len(bullet_lines):
            return _format_facet_query(_clean_facet(bullet_lines[target_idx])), {"status": "resolved_index"}
        if not prefer_bullets and 0 <= target_idx < len(s_qs):
            resolved_q = re.sub(r"^(?:\*\*\[.*?\]\*\*:\s*|\[.*?\]:?\s*)", "", s_qs[target_idx]).strip()
            return resolved_q, {"status": "resolved_suggested_question"}
        if 0 <= target_idx < len(s_qs):
            resolved_q = re.sub(r"^(?:\*\*\[.*?\]\*\*:\s*|\[.*?\]:?\s*)", "", s_qs[target_idx]).strip()
            return resolved_q, {"status": "resolved_suggested_question"}
        if 0 <= target_idx < len(bullet_lines):
            return _format_facet_query(_clean_facet(bullet_lines[target_idx])), {"status": "resolved_index"}

        if allow_clarification:
            return NEED_CLARIFICATION, {
                "status": NEED_CLARIFICATION,
                "reason": "index_out_of_range",
                "requested_index": target_idx + 1,
                "available_points": len(bullet_lines),
                "available_questions": len(s_qs),
            }
        return q_raw, {"status": "unchanged"}

    # Reference & pronoun vocabularies
    singular_pronouns = [
        "cái đó", "cái này", "điều này", "điều đó", "phần trên", "ở trên",
        "phần vừa rồi", "vừa nêu", "khái niệm đó", "khái niệm này",
        "chất đó", "chất này", "phương pháp này", "phương pháp đó",
        "công nghệ này", "công nghệ đó", "mô hình này", "mô hình đó",
        "hệ thống này", "hệ thống đó", "thuật toán này", "thuật toán đó",
        "công thức này", "công thức đó", "giao thức đó", "giao thức này",
        "thứ này", "thứ đó", "nó",
        "this method", "that method", "this system", "this model", "that one", "it",
    ]
    plural_pronouns = [
        "cả hai", "hai cái đó", "hai chất đó", "hai phương pháp đó", "chúng",
        "they", "these", "both of them",
    ]
    first_pos_refs = ["cái đầu tiên", "cái đầu", "vế đầu", "chất đầu", "ý đầu tiên", "ý đầu"]
    second_pos_refs = ["cái thứ hai", "cái sau", "vế sau", "chất sau", "chất thứ hai"]
    elliptical_starters = ["thế còn", "vậy còn", "thế thì", "còn", "what about", "how about"]
    vague_followup_only = [
        "giải thích thêm", "giải thích thêm chi tiết", "nói rõ hơn",
        "chi tiết hơn", "cho ví dụ cụ thể", "tại sao lại như vậy", "vì sao vậy",
    ]

    matched_singular = None
    if not _has_document_self_reference(q_lower):
        for p in singular_pronouns:
            if re.search(rf"(?<!\w){re.escape(p)}(?!\w)", q_lower):
                matched_singular = p
                break

    matched_plural = None
    for p in plural_pronouns:
        if re.search(rf"(?<!\w){re.escape(p)}(?!\w)", q_lower):
            matched_plural = p
            break

    matched_first_pos = next((p for p in first_pos_refs if re.search(rf"(?<!\w){re.escape(p)}(?!\w)", q_lower)), None)
    matched_second_pos = next((p for p in second_pos_refs if re.search(rf"(?<!\w){re.escape(p)}(?!\w)", q_lower)), None)
    starts_elliptical = any(q_lower.startswith(st + " ") or q_lower == st for st in elliptical_starters)
    is_vague_short = any(q_lower.strip(" ?.!").startswith(vf) for vf in vague_followup_only) and len(q_raw.split()) <= 8

    needs_prior_context = bool(
        matched_singular or matched_plural or matched_first_pos or matched_second_pos or starts_elliptical or is_vague_short
    )

    # Filter substantive prior user turns (exclude pure greetings or prior clarification-failed turns)
    _greetings = {"hello", "hi", "xin chào", "chào", "chào bạn", "chào ad", "cảm ơn", "thanks", "ok"}
    substantive_user_turns: List[str] = []
    for idx_m, m in enumerate(prior_msgs):
        if m.get("role") != "user":
            continue
        u_txt = (m.get("content") or "").strip()
        if not u_txt or u_txt.lower().strip(" !.?") in _greetings:
            continue
        # Skip if the immediate assistant reply to this user turn was CLARIFICATION_NEEDED
        if idx_m + 1 < len(prior_msgs) and prior_msgs[idx_m + 1].get("routing") == "CLARIFICATION_NEEDED":
            continue
        substantive_user_turns.append(u_txt)

    if not substantive_user_turns:
        if needs_prior_context and allow_clarification:
            return NEED_CLARIFICATION, {"status": NEED_CLARIFICATION, "reason": "missing_antecedent"}
        return q_raw, {"status": "standalone"}

    last_user_query = substantive_user_turns[-1]
    prior_constraints = _extract_prior_constraints(last_user_query)

    # 2. Topic anchor carry-over (e.g. 'topic 49', "'SA-CMS'") when current query has no explicit pronoun to substitute
    has_explicit_pronoun = bool(matched_singular or matched_plural or matched_first_pos or matched_second_pos)
    current_anchor = extract_topic_anchor(q_raw)
    if current_anchor is None and not has_explicit_pronoun and not _has_document_self_reference(q_lower):
        words = q_raw.split()
        if len(words) <= 14:
            generic_cues = ["này", "đó", "thêm", "chi tiết", "ví dụ", "tại sao", "như thế nào"]
            has_anaphoric_cue = (
                needs_prior_context
                or any(re.search(rf"(?<!\w){re.escape(c)}(?!\w)", q_lower) for c in generic_cues)
            )
            if has_anaphoric_cue:
                last_anchor = extract_topic_anchor(last_user_query)
                if last_anchor:
                    return f"{q_raw} ({last_anchor})", {"status": "anchor_carry_over", "anchor": last_anchor}

    if not needs_prior_context:
        return q_raw, {"status": "standalone"}

    # 3. Multi-entity disambiguation & positional resolution (Rule 2, Rule 5, Rule 7)
    multi_entities = _extract_multi_entities_from_turn(last_user_query)
    if len(multi_entities) >= 2:
        if matched_first_pos:
            rewritten = re.sub(rf"(?<!\w){re.escape(matched_first_pos)}(?!\w)", multi_entities[0], q_raw, count=1, flags=re.IGNORECASE)
            if prior_constraints and prior_constraints.lower() not in rewritten.lower():
                rewritten = f"{prior_constraints}, {rewritten}"
            return rewritten, {"status": "resolved_first_entity", "entity": multi_entities[0]}
        if matched_second_pos:
            rewritten = re.sub(rf"(?<!\w){re.escape(matched_second_pos)}(?!\w)", multi_entities[1], q_raw, count=1, flags=re.IGNORECASE)
            if prior_constraints and prior_constraints.lower() not in rewritten.lower():
                rewritten = f"{prior_constraints}, {rewritten}"
            return rewritten, {"status": "resolved_second_entity", "entity": multi_entities[1]}
        if matched_plural:
            joined_ents = " và ".join(multi_entities)
            rewritten = re.sub(rf"(?<!\w){re.escape(matched_plural)}(?!\w)", joined_ents, q_raw, count=1, flags=re.IGNORECASE)
            if prior_constraints and prior_constraints.lower() not in rewritten.lower():
                rewritten = f"{prior_constraints}, {rewritten}"
            return rewritten, {"status": "resolved_plural_entities", "entities": multi_entities}
        if matched_singular and allow_clarification:
            # Check if the user already named one of the entities explicitly in q_raw
            if not any(ent.lower() in q_lower for ent in multi_entities):
                return NEED_CLARIFICATION, {
                    "status": NEED_CLARIFICATION,
                    "reason": "ambiguous_multi_entity",
                    "candidates": multi_entities,
                }

    # 4. Extract clean primary subject from last_user_query while preserving prior_constraints separately (Rule 2 & 3)
    clean_last = last_user_query
    if prior_constraints:
        for pc in prior_constraints.split(","):
            clean_last = re.sub(re.escape(pc.strip()), "", clean_last, flags=re.IGNORECASE)
    for stop in [
        "hãy giải thích", "giải thích", "hãy trình bày", "trình bày", "cho tôi biết", "cho biết",
        "khái niệm về", "định nghĩa về", "nội dung về", "thông tin về",
        "là gì", "la gi", "như thế nào", "ra sao", "thế nào", "what is", "explain",
    ]:
        clean_last = re.sub(rf"(?<!\w){re.escape(stop)}(?!\w)", "", clean_last, flags=re.IGNORECASE)
    subject = re.sub(r"\s{2,}", " ", clean_last).strip(" ?:.,-!\"'")
    if not subject:
        subject = last_user_query.strip(" ?:.,-!\"'")

    target_ref = matched_singular or matched_plural
    if target_ref:
        if target_ref in ("phần trên", "ở trên", "phần vừa rồi", "vừa nêu"):
            replacement = f"nội dung về {subject}" if not q_lower.startswith(target_ref) else subject
        else:
            replacement = subject
        rewritten = re.sub(rf"(?<!\w){re.escape(target_ref)}(?!\w)", replacement, q_raw, count=1, flags=re.IGNORECASE)
    else:
        rewritten = f"{subject}: {q_raw}"

    if prior_constraints and prior_constraints.lower() not in rewritten.lower():
        rewritten = f"{prior_constraints}, {rewritten}"

    rewritten = re.sub(r"\s{2,}", " ", rewritten).strip()
    return rewritten, {"status": "rewritten", "subject": subject, "constraints": prior_constraints}


def rewrite_query_text(
    conversation_history: Sequence[Dict[str, Any]],
    current_question: str,
) -> str:
    """
    Exact prompt-spec adapter: returns ONLY the standalone rewritten query string,
    or 'NEED_CLARIFICATION' when the referent cannot be determined.
    """
    out, _ = rewrite_standalone_query(
        conversation_history=conversation_history,
        current_question=current_question,
        allow_clarification=True,
    )
    return out


def generate_title_from_query(query: str, existing_titles: Optional[Set[str]] = None) -> str:
    """
    Generates a concise, meaningful session title from a user query, avoiding duplicates.
    Examples:
      'Kiến trúc SA-CMS là gì?' -> 'Kiến trúc SA-CMS'
      'Cơ chế bộ nhớ L1 L2 L3 hoạt động thế nào?' -> 'Cơ chế bộ nhớ L1 L2 L3'
      'Giải thích về Nested Learning và CMS' -> 'Nested Learning và CMS'
    Avoids duplicate titles by adding a numeric suffix '(2)', '(3)' if necessary.
    Never exposes internal IDs.
    """
    clean = query.strip()
    clean = re.sub(r"\s+", " ", clean)

    # Conversational prefixes in Vietnamese and English
    prefixes = [
        "cho tôi biết về", "cho tôi biết", "cho em biết về", "cho em biết",
        "hãy giải thích về", "giải thích về", "giải thích",
        "hãy phân tích về", "phân tích về", "phân tích",
        "hãy tóm tắt về", "hãy tóm tắt", "tóm tắt về", "tóm tắt",
        "cho mình hỏi về", "cho mình hỏi", "xin hỏi về", "xin hỏi",
        "tìm hiểu về", "trình bày về", "trình bày",
        "hãy cho biết về", "hãy cho biết", "chi tiết về", "thông tin về",
        "bạn có thể cho biết", "bạn có biết",
        "what is", "explain", "tell me about", "summarize",
    ]
    for p in prefixes:
        if clean.lower().startswith(p):
            clean = clean[len(p):].strip()
            break

    # Strip trailing punctuation before checking question suffixes
    clean = clean.strip(" ?:.,-!\"'’“”[](){}")

    # Trailing question phrases
    suffixes = [
        "là gì vậy", "là gì", "như thế nào vậy", "như thế nào",
        "ra sao vậy", "ra sao", "hoạt động thế nào", "hoạt động ra sao",
        "thế nào", "đúng không", "phải không", "được không",
        "is it", "what is it",
    ]
    for _ in range(2):
        clean = clean.strip(" ?:.,-!\"'’“”[](){}")
        clean_lower = clean.lower()
        matched = False
        for s in suffixes:
            if clean_lower.endswith(s):
                clean = clean[:-len(s)].strip()
                matched = True
                break
        if not matched:
            break

    # Strip punctuation again
    clean = clean.strip(" ?:.,-!\"'’“”[](){}")

    if not clean:
        words = query.strip().split()
        clean = " ".join(words[:5]) if words else "Cuộc trò chuyện mới"

    # Truncate cleanly up to ~36 characters
    if len(clean) > 36:
        truncated = clean[:36]
        last_space = truncated.rfind(" ")
        if last_space > 15:
            clean = truncated[:last_space] + "..."
        else:
            clean = truncated + "..."

    # Capitalize first character
    clean = clean[:1].upper() + clean[1:]

    # Deduplicate against existing titles if provided
    if existing_titles:
        base_title = clean
        counter = 2
        while clean in existing_titles:
            clean = f"{base_title} ({counter})"
            counter += 1

    return clean


def extract_topic_anchor(text: str) -> Optional[str]:
    """
    Extracts explicit topic anchor (alias + number, or quoted text) from user query.
    Examples:
      'cho tôi biết topic 49' -> 'topic 49'
      'cho tôi biết chủ đề 47' -> 'chủ đề 47'
      'Nội dung liên quan đến "SA-CMS"' -> 'SA-CMS'
    """
    if not text:
        return None
    # 1. Topic aliases + number
    m = re.search(
        r"\b(topic|chủ\s*đề|bài|mục|chương|phần|section|chapter|lesson|unit)\s*(\d+)\b",
        text,
        re.IGNORECASE,
    )
    if m:
        alias = m.group(1).strip()
        num = m.group(2).strip()
        return f"{alias} {num}"

    # 2. Quoted text
    qm = re.search(r"['\"“]([^'\"”]+)['\"”]", text)
    if qm:
        val = qm.group(1).strip()
        if len(val) >= 2:
            return val
    return None


class ChatSession:
    """Represents an active multi-turn conversation session."""

    def __init__(
        self,
        session_id: str,
        title: str = "Cuộc trò chuyện mới",
        document_ids: Optional[List[str]] = None,
        created_at: Optional[float] = None,
        updated_at: Optional[float] = None,
        messages: Optional[List[Dict[str, Any]]] = None,
    ):
        self.session_id = session_id
        self.title = title
        self.document_ids = document_ids or []
        self.created_at = created_at or time.time()
        self.updated_at = updated_at or self.created_at
        self.messages = messages or []

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "title": self.title,
            "document_ids": self.document_ids,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "messages": self.messages,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChatSession":
        return cls(
            session_id=data["session_id"],
            title=data.get("title", "Cuộc trò chuyện mới"),
            document_ids=data.get("document_ids", []),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
            messages=data.get("messages", []),
        )

    def add_message(
        self,
        role: str,
        content: str,
        citations: Optional[List[Dict[str, Any]]] = None,
        evidence: Optional[List[Dict[str, Any]]] = None,
        telemetry: Optional[Dict[str, Any]] = None,
        routing: Optional[str] = None,
        refused: bool = False,
        refusal_reason: Optional[str] = None,
        diagnostics: Optional[Dict[str, Any]] = None,
        existing_titles: Optional[Set[str]] = None,
        suggested_questions: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        msg_id = f"msg_{uuid.uuid4().hex[:10]}"
        msg = {
            "id": msg_id,
            "role": role,
            "content": content,
            "timestamp": time.time(),
            "citations": citations or [],
            "evidence": evidence or [],
            "telemetry": telemetry or {},
            "routing": routing or "DIRECT_LOOKUP",
            "refused": refused,
            "refusal_reason": refusal_reason,
            "diagnostics": diagnostics or {},
            "suggested_questions": suggested_questions or [],
        }
        self.messages.append(msg)
        self.updated_at = time.time()

        # Auto-update session title based on first user message if default
        if role == "user" and (self.title in ("Cuộc trò chuyện mới", "New Chat", "") or not self.title):
            self.title = generate_title_from_query(content, existing_titles)

        return msg

    def add_system_event(
        self,
        event_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        msg_id = f"msg_{uuid.uuid4().hex[:10]}"
        msg = {
            "id": msg_id,
            "role": "system",
            "type": event_type,
            "content": content,
            "timestamp": time.time(),
            "metadata": metadata or {},
            "citations": [],
            "evidence": [],
            "telemetry": {},
            "routing": "SYSTEM_EVENT",
            "refused": False,
            "refusal_reason": None,
            "diagnostics": {},
        }
        self.messages.append(msg)
        self.updated_at = time.time()
        return msg

    def attach_document(self, doc_id: str) -> bool:
        if doc_id not in self.document_ids:
            self.document_ids.append(doc_id)
            self.updated_at = time.time()
            return True
        return False

    def detach_document(self, doc_id: str) -> bool:
        if doc_id in self.document_ids:
            self.document_ids.remove(doc_id)
            self.updated_at = time.time()
            return True
        return False


class SessionManager:
    """Manages chat session lifecycle, persistence, and conversation context."""

    def __init__(self, storage_dir: str = "data/chat_sessions"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_file = self.storage_dir / "sessions.json"
        self._sessions: Dict[str, ChatSession] = {}
        self._load_sessions()

    def _load_sessions(self):
        if self.sessions_file.exists():
            try:
                with open(self.sessions_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        session = ChatSession.from_dict(item)
                        self._sessions[session.session_id] = session
            except Exception:
                self._sessions = {}

    def _save_sessions(self):
        try:
            data = [s.to_dict() for s in self._sessions.values()]
            with open(self.sessions_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    def create_session(
        self,
        title: Optional[str] = None,
        document_ids: Optional[List[str]] = None,
    ) -> ChatSession:
        session_id = f"chat_{uuid.uuid4().hex[:12]}"
        session = ChatSession(
            session_id=session_id,
            title=title or "Cuộc trò chuyện mới",
            document_ids=document_ids or [],
        )
        self._sessions[session_id] = session
        self._save_sessions()
        return session

    def get_session(self, session_id: str) -> Optional[ChatSession]:
        return self._sessions.get(session_id)

    def get_existing_titles(self, exclude_session_id: Optional[str] = None) -> Set[str]:
        return {
            s.title for s_id, s in self._sessions.items()
            if s_id != exclude_session_id and s.title and s.title not in ("Cuộc trò chuyện mới", "New Chat")
        }

    def list_sessions(self) -> List[Dict[str, Any]]:
        # Sort newest first
        sorted_sessions = sorted(
            self._sessions.values(), key=lambda s: s.updated_at, reverse=True
        )
        now = time.time()
        one_day = 86400

        result = []
        for s in sorted_sessions:
            diff = now - s.updated_at
            if diff < one_day:
                group = "Hôm nay"
            elif diff < 2 * one_day:
                group = "Hôm qua"
            else:
                group = "Trước đó"

            result.append({
                "session_id": s.session_id,
                "title": s.title,
                "document_ids": s.document_ids,
                "created_at": s.created_at,
                "updated_at": s.updated_at,
                "message_count": len(s.messages),
                "time_group": group,
            })
        return result

    def rename_session(self, session_id: str, new_title: str) -> bool:
        session = self.get_session(session_id)
        if session:
            session.title = new_title.strip() or "Cuộc trò chuyện"
            session.updated_at = time.time()
            self._save_sessions()
            return True
        return False

    def delete_session(self, session_id: str) -> bool:
        if session_id in self._sessions:
            del self._sessions[session_id]
            self._save_sessions()
            return True
        return False

    def attach_document(self, session_id: str, doc_id: str) -> bool:
        session = self.get_session(session_id)
        if session:
            attached = session.attach_document(doc_id)
            if attached:
                self._save_sessions()
            return True
        return False

    def record_document_event(
        self,
        session_id: str,
        doc_id: str,
        title: str,
        file_name: Optional[str] = None,
        file_size: Optional[str] = None,
        source: str = "upload",
    ) -> Optional[Dict[str, Any]]:
        session = self.get_session(session_id)
        if not session:
            return None

        display_title = title or file_name or doc_id
        content = f"Đã thêm tài liệu \"{display_title}\" vào cuộc trò chuyện."
        event = session.add_system_event(
            event_type="document_attached",
            content=content,
            metadata={
                "document_id": doc_id,
                "title": display_title,
                "file_name": file_name or display_title,
                "file_size": file_size,
                "source": source,
            },
        )
        self._save_sessions()
        return event

    def detach_document(self, session_id: str, doc_id: str) -> bool:
        session = self.get_session(session_id)
        if session:
            detached = session.detach_document(doc_id)
            if detached:
                self._save_sessions()
            return True
        return False

    def save(self):
        self._save_sessions()

    def resolve_conversation_context_with_meta(
        self,
        session_id: str,
        current_query: str,
        allow_clarification: bool = True,
    ) -> Tuple[str, Dict[str, Any]]:
        """Resolves follow-up queries with structured rewrite metadata and NEED_CLARIFICATION support."""
        session = self.get_session(session_id)
        history = session.messages if session and session.messages else []
        return rewrite_standalone_query(
            conversation_history=history,
            current_question=current_query,
            allow_clarification=allow_clarification,
        )

    def resolve_conversation_context(
        self,
        session_id: str,
        current_query: str,
        allow_clarification: bool = False,
    ) -> str:
        """
        Task 12: Resolves follow-up pronouns, numbered questions ("câu 2", "ý 2"), prior constraints,
        and elliptical queries using conversation history.
        """
        resolved, _ = self.resolve_conversation_context_with_meta(
            session_id=session_id,
            current_query=current_query,
            allow_clarification=allow_clarification,
        )
        return resolved
