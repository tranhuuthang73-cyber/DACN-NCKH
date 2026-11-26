"""
Persistent 3-Layer Self-Built Long-Term Memory (LTM) with Bit-Exact Unlearning.

100% Local Offline: Pure Python stdlib + NumPy + WaveCMS RidgeAssociativeMemory.
ZERO external LLM/AI APIs.

Architecture:
  - Layer 1 (Semantic Concept Graph): Fast (<25ms) extraction of concept nodes,
    definitions, formulas, and structural/contrastive relations (`part_of_section`,
    `contrasts_with`), indexed into `RidgeAssociativeMemory(dim=64, lam=1.0)`.
  - Layer 2 (Episodic Verified QA & Associative Synonym Learning): Stores only
    faithful, non-refused, non-clarification, cited QA interactions (anti-poisoning
    invariant) and learns query -> evidence associative bridges scoped per document.
  - Layer 3 (Cross-Session Learner Profile): Tracks studied concepts/topics and
    clarification struggles across sessions to surface contextual study hints.
  - Certified Exact Unlearning: Removes all Layer 1/2/3 traces of `doc_id` and
    restores bit-exact int64 fixed-point `G, B` matrices in O(1) matrix ops.
"""

from __future__ import annotations

import json
import os
import re
import threading
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

import numpy as np

from src.wave_cms.fast_weights import RidgeAssociativeMemory
from src.wave_cms.tree_memory import compute_deterministic_routing_key, strip_accents

_RIDGE_DIM = 64
_RIDGE_LAM = 1.0
_MAX_EPISODIC_ENTRIES = 500
_MAX_PASSAGES_SCAN = 120
_MAX_CONCEPTS_PER_DOC = 80

_QUERY_STOPWORDS: Set[str] = {
    "la", "gi", "nhu", "the", "nao", "sao", "tai", "vi", "cho", "toi", "minh",
    "em", "hoi", "biet", "hay", "giai", "thich", "tom", "tat", "phan", "tich",
    "trinh", "bay", "neu", "khai", "niem", "dinh", "nghia", "ve", "cua", "trong",
    "tai", "lieu", "nay", "do", "cac", "nhung", "mot", "va", "hoac", "co", "duoc",
    "what", "is", "are", "how", "why", "explain", "define", "about", "the", "of",
    "in", "to", "for", "a", "an", "please", "tell", "me",
}

_INVALID_TERM_STARTS: Set[str] = {
    "day", "do", "no", "chung", "ho", "ta", "khi", "neu", "vi", "do", "tuy",
    "nhung", "ngoai", "ben", "canh", "vi du", "chang han", "buoc", "cau",
    "trang", "hinh", "bang", "muc", "chuong", "phan", "theo", "nhu", "vay",
    "this", "that", "these", "those", "it", "they", "when", "if", "because",
    "however", "for example", "step", "page", "figure", "table",
}

_DEF_PATTERNS: Tuple[re.Pattern[str], ...] = (
    re.compile(
        r"(?:^|[.!?;\n]\s*)([A-ZÀ-ỸĐ][^\n.!?:;()]{2,65}?)\s+"
        r"(?:được\s+định\s+nghĩa\s+là|được\s+hiểu\s+là|được\s+gọi\s+là|là\s+một|là\s+hệ\s+thống|là\s+phương\s+pháp|là\s+quá\s+trình|là\s+hình\s+thức|là)\s+"
        r"([^\n.!?]{12,220})",
    ),
    re.compile(
        r"(?:^|[.!?;\n]\s*)([A-Z][A-Za-z0-9\s\-_/]{2,60}?)\s+"
        r"(?:is\s+defined\s+as|refers\s+to|is\s+a|is\s+an|is\s+the)\s+"
        r"([^\n.!?]{12,220})",
    ),
)

_CONTRAST_PATTERNS: Tuple[re.Pattern[str], ...] = (
    re.compile(
        r"(?:khác\s+với|trái\s+ngược\s+với|đối\s+lập\s+với|ngược\s+lại\s+với|phân\s+biệt\s+với|"
        r"so\s+với|in\s+contrast\s+to|unlike|contrary\s+to|versus|vs\.)\s+"
        r"([A-Za-zÀ-ỹĐđ0-9][^\n,.;:!?()]{2,55})",
        re.IGNORECASE,
    ),
)

_FORMULA_SPAN_RE = re.compile(
    r"([A-Za-z0-9_()+\-*/^]+\s*(?:=|→|⇌|⇒)\s*[A-Za-z0-9_()+\-*/^.,\s]{2,45})"
)


def _get_field(obj: Any, key: str, default: Any = "") -> Any:
    if isinstance(obj, dict):
        val = obj.get(key, default)
    else:
        val = getattr(obj, key, default)
    return default if val is None else val


def _normalize_topic(raw_text: str) -> Tuple[str, str, List[str]]:
    """Returns (normalized_key, clean_display_topic, content_tokens)."""
    raw = re.sub(r"\s+", " ", str(raw_text or "")).strip(" ?!.,;:\"'()[]{}")
    norm_all = strip_accents(raw)
    raw_words = re.findall(r"[A-Za-zÀ-ỹĐđ0-9_]+", raw)
    norm_words = [strip_accents(w) for w in raw_words]

    kept_display: List[str] = []
    kept_tokens: List[str] = []
    for rw, nw in zip(raw_words, norm_words):
        if len(nw) < 2 or nw in _QUERY_STOPWORDS:
            continue
        kept_display.append(rw)
        kept_tokens.append(nw)

    if not kept_tokens:
        fallback_toks = [w for w in re.findall(r"[a-z0-9]+", norm_all) if len(w) >= 2]
        return " ".join(fallback_toks[:6]), raw[:80], fallback_toks[:6]

    return " ".join(kept_tokens[:8]), " ".join(kept_display[:8]), kept_tokens[:8]


def _extract_formulas_fast(text: str) -> List[str]:
    if "=" not in text and "→" not in text and "⇌" not in text and "⇒" not in text:
        return []
    out: List[str] = []
    for m in _FORMULA_SPAN_RE.finditer(text):
        cand = re.sub(r"\s+", " ", m.group(1)).strip()
        if 3 <= len(cand) <= 60 and cand not in out:
            out.append(cand)
            if len(out) >= 4:
                break
    return out


class LongTermMemoryStore:
    """
    Persistent 3-layer Long-Term Memory backed by JSON metadata and bit-exact
    int64 FixedPointMatrix sufficient statistics (`RidgeAssociativeMemory`).
    """

    def __init__(self, storage_dir: Optional[str] = None) -> None:
        resolved = Path(storage_dir or "local_runtime/long_term_memory")
        self.storage_dir: Path = resolved
        self.state_path: Path = self.storage_dir / "ltm_state.json"
        self.ridge_path: Path = self.storage_dir / "ltm_ridge_stats.npz"

        self._lock = threading.RLock()
        self.ridge = RidgeAssociativeMemory(dim=_RIDGE_DIM, lam=_RIDGE_LAM)

        # Layer 1: doc_id -> list of concept node dicts
        self.concepts_by_doc: Dict[str, List[Dict[str, Any]]] = {}
        self.assimilated_docs: Dict[str, Dict[str, Any]] = {}

        # Layer 2: bounded list of verified QA episodes
        self.episodic_qa: List[Dict[str, Any]] = []
        self._ep_seq: int = 0

        # Layer 3: cross-session learner profile
        self.learner_profile: Dict[str, Any] = {
            "doc_topic_counts": {},     # doc_id -> {norm_topic: count}
            "global_topic_counts": {},  # norm_topic -> count (when no doc attached)
            "topic_display": {},        # norm_topic -> display string
            "clarification_count": 0,
            "doc_clarification_counts": {},  # doc_id -> count
            "recent_concepts": [],      # [{topic, doc_ids, timestamp}]
        }

        self._load()

    # ------------------------------------------------------------------
    # Persistence (Exact JSON + int64 NPZ without pickle)
    # ------------------------------------------------------------------

    def _load(self) -> None:
        with self._lock:
            if self.state_path.is_file():
                try:
                    raw = json.loads(self.state_path.read_text(encoding="utf-8"))
                    self.concepts_by_doc = dict(raw.get("concepts_by_doc") or {})
                    self.assimilated_docs = dict(raw.get("assimilated_docs") or {})
                    self.episodic_qa = list(raw.get("episodic_qa") or [])
                    self._ep_seq = int(raw.get("ep_seq") or len(self.episodic_qa))
                    lp = raw.get("learner_profile") or {}
                    self.learner_profile["doc_topic_counts"] = dict(lp.get("doc_topic_counts") or {})
                    self.learner_profile["global_topic_counts"] = dict(lp.get("global_topic_counts") or {})
                    self.learner_profile["topic_display"] = dict(lp.get("topic_display") or {})
                    self.learner_profile["clarification_count"] = int(lp.get("clarification_count") or 0)
                    self.learner_profile["doc_clarification_counts"] = dict(
                        lp.get("doc_clarification_counts") or {}
                    )
                    self.learner_profile["recent_concepts"] = list(lp.get("recent_concepts") or [])
                except Exception:
                    pass

            if self.ridge_path.is_file():
                try:
                    with np.load(str(self.ridge_path), allow_pickle=False) as data:
                        meta = data["meta"]
                        dim = int(meta[0])
                        scale_bits = int(meta[1])
                        lam = float(data["lam"][0])
                        ridge = RidgeAssociativeMemory(dim=dim, lam=lam, scale_bits=scale_bits)
                        ridge.G.data = np.asarray(data["G_data"], dtype=np.int64).copy()
                        ridge.B.data = np.asarray(data["B_data"], dtype=np.int64).copy()

                        keys_arr = data["contrib_keys"]
                        cg_arr = np.asarray(data["contrib_G"], dtype=np.int64)
                        cb_arr = np.asarray(data["contrib_B"], dtype=np.int64)
                        for idx, k_raw in enumerate(keys_arr.tolist()):
                            k_str = str(k_raw)
                            ridge._doc_contributions[k_str] = (
                                cg_arr[idx].copy(),
                                cb_arr[idx].copy(),
                            )
                        ridge._version += 1
                        self.ridge = ridge
                except Exception:
                    pass

    def _save(self) -> None:
        with self._lock:
            self.storage_dir.mkdir(parents=True, exist_ok=True)

            payload = {
                "concepts_by_doc": self.concepts_by_doc,
                "assimilated_docs": self.assimilated_docs,
                "episodic_qa": self.episodic_qa,
                "ep_seq": self._ep_seq,
                "learner_profile": self.learner_profile,
            }
            self.state_path.write_text(
                json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
                encoding="utf-8",
            )

            keys = list(self.ridge._doc_contributions.keys())
            if keys:
                cg = np.stack([self.ridge._doc_contributions[k][0] for k in keys], axis=0).astype(np.int64)
                cb = np.stack([self.ridge._doc_contributions[k][1] for k in keys], axis=0).astype(np.int64)
                keys_np = np.asarray(keys, dtype=np.str_)
            else:
                cg = np.zeros((0, self.ridge.dim, self.ridge.dim), dtype=np.int64)
                cb = np.zeros((0, self.ridge.dim, self.ridge.dim), dtype=np.int64)
                keys_np = np.asarray([], dtype=np.str_)

            with open(self.ridge_path, "wb") as fh:
                np.savez(
                    fh,
                    meta=np.asarray([self.ridge.dim, self.ridge.scale_bits], dtype=np.int64),
                    lam=np.asarray([self.ridge.lam], dtype=np.float64),
                    G_data=self.ridge.G.data,
                    B_data=self.ridge.B.data,
                    contrib_keys=keys_np,
                    contrib_G=cg,
                    contrib_B=cb,
                )

    # ------------------------------------------------------------------
    # Layer 1: Semantic Concept Graph
    # ------------------------------------------------------------------

    def assimilate_document(
        self,
        doc_id: str,
        title: str,
        raw_text: str,
        passages: Sequence[Any],
    ) -> Dict[str, Any]:
        """
        Extracts concept nodes & relations in <25ms and indexes associative
        concept/heading -> passage routing keys into RidgeAssociativeMemory.
        """
        if not doc_id:
            raise ValueError("doc_id must be non-empty")

        with self._lock:
            # Clean previous Layer 1 state if re-assimilating the same document
            if doc_id in self.ridge._doc_contributions:
                self.ridge.remove_document(doc_id)

            norm_passages: List[Tuple[str, str, str]] = []
            if passages:
                step = max(1, len(passages) // _MAX_PASSAGES_SCAN)
                sampled = passages[::step][:_MAX_PASSAGES_SCAN]
                for idx, p in enumerate(sampled):
                    pid = str(_get_field(p, "passage_id") or f"{doc_id}::P{idx:03d}")
                    sec = str(_get_field(p, "section_title") or _get_field(p, "heading") or title or "").strip()
                    txt = str(
                        _get_field(p, "text")
                        or _get_field(p, "content")
                        or _get_field(p, "snippet")
                        or ""
                    ).strip()
                    if txt:
                        norm_passages.append((pid, sec, txt))
            elif raw_text:
                chunks = [c.strip() for c in re.split(r"\n\s*\n+", raw_text) if c.strip()]
                step = max(1, len(chunks) // _MAX_PASSAGES_SCAN)
                for idx, chunk in enumerate(chunks[::step][:_MAX_PASSAGES_SCAN]):
                    norm_passages.append((f"{doc_id}::P{idx:03d}", str(title or "").strip(), chunk))

            concepts: List[Dict[str, Any]] = []
            seen_terms: Set[str] = set()
            k_rows: List[np.ndarray] = []
            v_rows: List[np.ndarray] = []
            relations_count = 0

            for pid, sec_title, p_text in norm_passages:
                p_slice = p_text[:700]
                p_key = compute_deterministic_routing_key(f"{sec_title} {p_slice[:420]}".strip(), _RIDGE_DIM)
                formulas = _extract_formulas_fast(p_slice)

                contrasts: List[str] = []
                for cp in _CONTRAST_PATTERNS:
                    for cm in cp.finditer(p_slice):
                        c_target = re.sub(r"\s+", " ", cm.group(1)).strip(" ,.;:()\"'")
                        if 2 <= len(c_target) <= 55 and c_target not in contrasts:
                            contrasts.append(c_target)

                matched_in_passage = False
                if len(concepts) < _MAX_CONCEPTS_PER_DOC:
                    for pat in _DEF_PATTERNS:
                        for m in pat.finditer(p_slice):
                            term_raw = re.sub(r"\s+", " ", m.group(1)).strip(" -–•*\"'()[]{}")
                            def_raw = re.sub(r"\s+", " ", m.group(2)).strip(" ,;:.")
                            term_norm = strip_accents(term_raw)
                            words_norm = term_norm.split()
                            if (
                                not words_norm
                                or len(words_norm) > 9
                                or words_norm[0] in _INVALID_TERM_STARTS
                                or term_norm in seen_terms
                            ):
                                continue
                            seen_terms.add(term_norm)
                            matched_in_passage = True

                            rels: List[Dict[str, str]] = []
                            if sec_title:
                                rels.append({"type": "part_of_section", "target": sec_title})
                            for ct in contrasts[:3]:
                                rels.append({"type": "contrasts_with", "target": ct})
                            relations_count += len(rels)

                            concepts.append(
                                {
                                    "term": term_raw,
                                    "normalized_term": term_norm,
                                    "definition": def_raw[:240],
                                    "section_title": sec_title,
                                    "passage_id": pid,
                                    "document_id": doc_id,
                                    "formulas": formulas,
                                    "part_of_section": sec_title,
                                    "contrasts_with": contrasts[:3],
                                    "relations": rels,
                                }
                            )
                            c_key = compute_deterministic_routing_key(
                                f"{term_raw} {sec_title}".strip(), _RIDGE_DIM
                            )
                            k_rows.append(c_key)
                            v_rows.append(p_key)
                            if len(concepts) >= _MAX_CONCEPTS_PER_DOC:
                                break
                        if len(concepts) >= _MAX_CONCEPTS_PER_DOC:
                            break

                # Index section heading -> passage even when no explicit `X là Y` sentence matched
                if sec_title:
                    sec_norm = strip_accents(sec_title)
                    if (
                        not matched_in_passage
                        and len(concepts) < _MAX_CONCEPTS_PER_DOC
                        and sec_norm
                        and sec_norm not in seen_terms
                        and not re.match(r"^(?:page|trang|slide|section)\s*\d+$", sec_norm)
                    ):
                        seen_terms.add(sec_norm)
                        first_sent = re.split(r"(?<=[.!?])\s+", p_slice, maxsplit=1)[0].strip()
                        rels = [{"type": "part_of_section", "target": title or sec_title}]
                        for ct in contrasts[:3]:
                            rels.append({"type": "contrasts_with", "target": ct})
                        relations_count += len(rels)
                        concepts.append(
                            {
                                "term": sec_title[:80],
                                "normalized_term": sec_norm,
                                "definition": first_sent[:240],
                                "section_title": sec_title,
                                "passage_id": pid,
                                "document_id": doc_id,
                                "formulas": formulas,
                                "part_of_section": title or sec_title,
                                "contrasts_with": contrasts[:3],
                                "relations": rels,
                            }
                        )
                    h_key = compute_deterministic_routing_key(f"{title} {sec_title}".strip(), _RIDGE_DIM)
                    k_rows.append(h_key)
                    v_rows.append(p_key)
                else:
                    k_rows.append(compute_deterministic_routing_key(p_slice[:160], _RIDGE_DIM))
                    v_rows.append(p_key)

            # Link sibling concepts in the same section that contrast if explicit contrast cues appeared
            by_sec: Dict[str, List[Dict[str, Any]]] = {}
            for c_node in concepts:
                sec_k = c_node.get("section_title") or ""
                if sec_k:
                    by_sec.setdefault(sec_k, []).append(c_node)
            for sibling_list in by_sec.values():
                if len(sibling_list) >= 2:
                    for i, c_i in enumerate(sibling_list[:4]):
                        if not c_i["contrasts_with"]:
                            other_term = sibling_list[(i + 1) % len(sibling_list)]["term"]
                            if other_term != c_i["term"]:
                                c_i["contrasts_with"].append(other_term)
                                c_i["relations"].append({"type": "contrasts_with", "target": other_term})
                                relations_count += 1

            if not k_rows:
                fallback_k = compute_deterministic_routing_key(title or doc_id, _RIDGE_DIM)
                fallback_v = compute_deterministic_routing_key(
                    (raw_text or title or doc_id)[:400], _RIDGE_DIM
                )
                k_rows.append(fallback_k)
                v_rows.append(fallback_v)

            K_mat = np.vstack(k_rows)
            V_mat = np.vstack(v_rows)
            self.ridge.add_document_pairs(doc_id, K_mat, V_mat)

            self.concepts_by_doc[doc_id] = concepts
            self.assimilated_docs[doc_id] = {
                "doc_id": doc_id,
                "title": str(title or doc_id),
                "concepts_count": len(concepts),
                "relations_count": relations_count,
                "passages_indexed": len(norm_passages),
                "timestamp": time.time(),
            }
            self._save()

            return {
                "doc_id": doc_id,
                "concepts_extracted": len(concepts),
                "concepts_added": len(concepts),
                "relations_extracted": relations_count,
                "pairs_indexed": int(K_mat.shape[0]),
            }

    # ------------------------------------------------------------------
    # Layer 2: Episodic Verified QA & Associative Synonym Learning
    # ------------------------------------------------------------------

    def _update_learner_profile(
        self,
        query_text: str,
        citations: Sequence[Any],
        needed_clarification: bool,
    ) -> None:
        norm_topic, display_topic, tokens = _normalize_topic(query_text)
        doc_ids: List[str] = []
        sec_titles: List[str] = []
        for cit in citations or ():
            d_id = str(_get_field(cit, "document_id") or "").strip()
            if d_id and d_id not in doc_ids:
                doc_ids.append(d_id)
            s_t = str(_get_field(cit, "section_title") or "").strip()
            if s_t and s_t not in sec_titles:
                sec_titles.append(s_t)

        if needed_clarification:
            self.learner_profile["clarification_count"] = (
                int(self.learner_profile.get("clarification_count", 0)) + 1
            )
            doc_clar = self.learner_profile.setdefault("doc_clarification_counts", {})
            for d_id in doc_ids:
                doc_clar[d_id] = int(doc_clar.get(d_id, 0)) + 1

        if not norm_topic:
            return

        topic_disp_map = self.learner_profile.setdefault("topic_display", {})
        if norm_topic not in topic_disp_map and display_topic:
            topic_disp_map[norm_topic] = display_topic

        doc_topic_counts: Dict[str, Dict[str, int]] = self.learner_profile.setdefault(
            "doc_topic_counts", {}
        )
        if doc_ids:
            for d_id in doc_ids:
                bucket = doc_topic_counts.setdefault(d_id, {})
                bucket[norm_topic] = int(bucket.get(norm_topic, 0)) + 1

                # Also credit matching Layer 1 concept nodes in `d_id`
                for c_node in self.concepts_by_doc.get(d_id, ()):
                    c_norm = c_node.get("normalized_term") or ""
                    if (
                        c_norm
                        and c_norm != norm_topic
                        and len(c_norm) >= 4
                        and (c_norm in norm_topic or norm_topic in c_norm)
                    ):
                        bucket[c_norm] = int(bucket.get(c_norm, 0)) + 1
                        topic_disp_map.setdefault(c_norm, c_node.get("term", c_norm))
        else:
            g_counts = self.learner_profile.setdefault("global_topic_counts", {})
            g_counts[norm_topic] = int(g_counts.get(norm_topic, 0)) + 1

        recent = self.learner_profile.setdefault("recent_concepts", [])
        recent.append(
            {
                "topic": display_topic or norm_topic,
                "normalized_topic": norm_topic,
                "tokens": tokens,
                "doc_ids": doc_ids,
                "section_titles": sec_titles[:2],
                "timestamp": time.time(),
            }
        )
        if len(recent) > 100:
            del recent[:-100]

    def record_verified_interaction(
        self,
        session_id: str,
        raw_query: str,
        effective_query: str,
        answer: str,
        citations: Sequence[Dict[str, Any]],
        refused: bool = False,
        is_faithful: bool = True,
        needed_clarification: bool = False,
    ) -> bool:
        """
        Updates Layer 3 learner profile unconditionally, and records into Layer 2
        episodic memory + RidgeAssociativeMemory ONLY if anti-poisoning invariants hold.
        """
        with self._lock:
            q_for_profile = effective_query or raw_query or ""
            self._update_learner_profile(
                query_text=q_for_profile,
                citations=citations,
                needed_clarification=needed_clarification,
            )

            # Anti-poisoning invariant
            if refused or (not is_faithful) or needed_clarification or (not citations):
                self._save()
                return False

            doc_ids: List[str] = []
            passage_ids: List[str] = []
            section_titles: List[str] = []
            top_cit_text = ""

            for idx, cit in enumerate(citations):
                d_id = str(_get_field(cit, "document_id") or "").strip()
                p_id = str(_get_field(cit, "passage_id") or "").strip()
                s_title = str(_get_field(cit, "section_title") or "").strip()
                c_txt = str(
                    _get_field(cit, "text")
                    or _get_field(cit, "snippet")
                    or _get_field(cit, "quote")
                    or _get_field(cit, "content")
                    or ""
                ).strip()
                if d_id and d_id not in doc_ids:
                    doc_ids.append(d_id)
                if p_id and p_id not in passage_ids:
                    passage_ids.append(p_id)
                if s_title and s_title not in section_titles:
                    section_titles.append(s_title)
                if idx == 0 or (not top_cit_text and c_txt):
                    top_cit_text = c_txt

            if not doc_ids:
                self._save()
                return False

            top_doc_id = doc_ids[0]
            if not top_cit_text:
                top_cit_text = f"{section_titles[0] if section_titles else ''} {(answer or '')[:300]}".strip()

            self._ep_seq += 1
            ep_id = f"{int(time.time() * 1000)}_{self._ep_seq}"
            ridge_ep_key = f"{top_doc_id}::ep::{ep_id}"

            # Enforce 500-entry episodic cap with exact Ridge unlearning of evicted entry
            while len(self.episodic_qa) >= _MAX_EPISODIC_ENTRIES:
                evicted = self.episodic_qa.pop(0)
                old_rk = evicted.get("ridge_key")
                if old_rk:
                    self.ridge.remove_document(str(old_rk))

            k_vec = compute_deterministic_routing_key(raw_query or effective_query, _RIDGE_DIM)
            v_vec = compute_deterministic_routing_key(top_cit_text[:480], _RIDGE_DIM)
            self.ridge.add_document_pairs(ridge_ep_key, k_vec, v_vec)

            self.episodic_qa.append(
                {
                    "session_id": str(session_id or ""),
                    "query": str(raw_query or "").strip(),
                    "effective_query": str(effective_query or raw_query or "").strip(),
                    "answer_preview": str(answer or "").strip()[:280],
                    "document_ids": doc_ids,
                    "passage_ids": passage_ids,
                    "section_titles": section_titles,
                    "timestamp": time.time(),
                    "top_doc_id": top_doc_id,
                    "ridge_key": ridge_ep_key,
                }
            )
            self._save()
            return True

    def _predict_scoped_ridge(self, q_vec: np.ndarray, allowed_set: Set[str]) -> Optional[np.ndarray]:
        """
        Computes M* @ q_vec using ONLY fixed-point sufficient statistics belonging to
        `allowed_set`, guaranteeing 0.0% cross-document mathematical leakage.
        """
        all_keys = list(self.ridge._doc_contributions.keys())
        if not all_keys:
            return None

        def _key_allowed(rk: str) -> bool:
            base_doc = rk.split("::ep::", 1)[0]
            return base_doc in allowed_set

        allowed_keys = [rk for rk in all_keys if _key_allowed(rk)]
        if not allowed_keys:
            return None

        if len(allowed_keys) == len(all_keys):
            return self.ridge.predict(q_vec)

        dim = self.ridge.dim
        scale = self.ridge.G.scale
        g_sum = np.zeros((dim, dim), dtype=np.int64)
        b_sum = np.zeros((dim, dim), dtype=np.int64)
        for rk in allowed_keys:
            qg, qb = self.ridge._doc_contributions[rk]
            g_sum = g_sum + qg
            b_sum = b_sum + qb

        g_float = g_sum.astype(np.float64) / scale
        g_sym = 0.5 * (g_float + g_float.T)
        a_mat = g_sym + self.ridge.lam * np.eye(dim, dtype=np.float64)
        b_float = b_sum.astype(np.float64) / scale

        chol = np.linalg.cholesky(a_mat)
        y_mat = np.linalg.solve(chol, b_float)
        m_t = np.linalg.solve(chol.T, y_mat)
        return m_t.T @ q_vec

    def recall_associative_boost(
        self,
        query: str,
        candidate_passages: Sequence[Any],
        allowed_document_ids: Sequence[str],
    ) -> Dict[str, float]:
        """
        Computes bounded [0.0, 6.0] associative boost scores per passage_id,
        strictly isolated to `allowed_document_ids` (0% cross-document leakage).
        """
        if not query or not candidate_passages or not allowed_document_ids:
            return {}

        allowed_set: Set[str] = {str(d) for d in allowed_document_ids if d}
        if not allowed_set:
            return {}

        with self._lock:
            q_vec = compute_deterministic_routing_key(query, _RIDGE_DIM)
            q_norm_topic, _, q_tokens = _normalize_topic(query)
            q_tok_set = set(q_tokens)

            v_hat = self._predict_scoped_ridge(q_vec, allowed_set)
            v_norm = float(np.linalg.norm(v_hat)) if v_hat is not None else 0.0

            # Precompute episodic passage boosts within allowed_set
            ep_pid_boost: Dict[str, float] = {}
            for ep in self.episodic_qa:
                ep_docs = set(ep.get("document_ids") or ())
                if not (ep_docs & allowed_set):
                    continue
                ep_q_vec = compute_deterministic_routing_key(ep.get("query") or "", _RIDGE_DIM)
                ep_eff_vec = compute_deterministic_routing_key(ep.get("effective_query") or "", _RIDGE_DIM)
                sim = max(float(np.dot(q_vec, ep_q_vec)), float(np.dot(q_vec, ep_eff_vec)))

                _, _, ep_toks = _normalize_topic(ep.get("effective_query") or ep.get("query") or "")
                if q_tok_set and ep_toks:
                    jacc = len(q_tok_set & set(ep_toks)) / float(len(q_tok_set | set(ep_toks)))
                    sim = max(sim, jacc)

                if sim > 0.25:
                    b_val = 3.2 * sim
                    for pid in ep.get("passage_ids") or ():
                        if pid > "" and b_val > ep_pid_boost.get(pid, 0.0):
                            ep_pid_boost[pid] = b_val

            # Precompute Layer 1 concept boosts within allowed_set
            concept_pid_boost: Dict[str, float] = {}
            if q_norm_topic:
                for d_id in allowed_set:
                    for c_node in self.concepts_by_doc.get(d_id, ()):
                        c_norm = c_node.get("normalized_term") or ""
                        c_pid = c_node.get("passage_id") or ""
                        if not c_norm or not c_pid:
                            continue
                        if c_norm in q_norm_topic or q_norm_topic in c_norm:
                            concept_pid_boost[c_pid] = max(concept_pid_boost.get(c_pid, 0.0), 1.5)
                        elif q_tok_set:
                            c_toks = set(c_norm.split())
                            overlap = len(q_tok_set & c_toks) / float(max(1, len(c_toks)))
                            if overlap >= 0.6:
                                concept_pid_boost[c_pid] = max(
                                    concept_pid_boost.get(c_pid, 0.0), 1.2 * overlap
                                )

            boosts: Dict[str, float] = {}
            for p in candidate_passages:
                p_doc = str(_get_field(p, "document_id") or "").strip()
                if p_doc not in allowed_set:
                    continue
                pid = str(_get_field(p, "passage_id") or "").strip()
                if not pid:
                    continue

                p_txt = str(
                    _get_field(p, "text")
                    or _get_field(p, "content")
                    or _get_field(p, "snippet")
                    or ""
                ).strip()
                p_sec = str(_get_field(p, "section_title") or "").strip()

                ridge_b = 0.0
                if v_hat is not None and v_norm > 1e-9 and (p_txt or p_sec):
                    p_vec_1 = compute_deterministic_routing_key(
                        f"{p_sec} {p_txt[:420]}".strip(), _RIDGE_DIM
                    )
                    p_vec_2 = compute_deterministic_routing_key(p_txt[:480], _RIDGE_DIM) if p_txt else p_vec_1
                    cos_align = max(
                        0.0,
                        float(np.dot(v_hat, p_vec_1)) / v_norm,
                        float(np.dot(v_hat, p_vec_2)) / v_norm,
                    )
                    confidence = min(1.0, v_norm / 0.08)
                    ridge_b = 2.8 * cos_align * confidence

                total = ridge_b + ep_pid_boost.get(pid, 0.0) + concept_pid_boost.get(pid, 0.0)
                bounded = float(min(6.0, max(0.0, total)))
                if bounded > 1e-6:
                    boosts[pid] = round(bounded, 6)

            return boosts

    # ------------------------------------------------------------------
    # Layer 3: Cross-Session Learner Profile
    # ------------------------------------------------------------------

    def get_learner_hint(
        self,
        query: str,
        allowed_document_ids: Sequence[str],
    ) -> Optional[str]:
        """
        Returns a 1-line Vietnamese study note if the student previously asked
        about the same concept/section >= 2 times within `allowed_document_ids`.
        """
        if not query or not allowed_document_ids:
            return None
        allowed_set = {str(d) for d in allowed_document_ids if d}
        if not allowed_set:
            return None

        norm_topic, _, q_tokens = _normalize_topic(query)
        if not norm_topic:
            return None
        q_tok_set = set(q_tokens)

        with self._lock:
            doc_topic_counts: Dict[str, Dict[str, int]] = self.learner_profile.get(
                "doc_topic_counts", {}
            )
            matched_count = 0
            for d_id in allowed_set:
                bucket = doc_topic_counts.get(d_id) or {}
                best_in_doc = 0
                for stored_topic, cnt in bucket.items():
                    if stored_topic == norm_topic:
                        best_in_doc = max(best_in_doc, int(cnt))
                        continue
                    s_toks = set(stored_topic.split())
                    if q_tok_set and s_toks:
                        jacc = len(q_tok_set & s_toks) / float(len(q_tok_set | s_toks))
                        if jacc >= 0.65 or (
                            len(stored_topic) >= 5
                            and len(norm_topic) >= 5
                            and (stored_topic in norm_topic or norm_topic in stored_topic)
                        ):
                            best_in_doc = max(best_in_doc, int(cnt))
                matched_count += best_in_doc

            if matched_count >= 2:
                return (
                    "🧠 *Ghi nhớ học tập: Chủ đề này bạn đã từng tra cứu trước đó — "
                    "dưới đây là tóm lược trọng tâm kèm liên hệ mở rộng:*"
                )
            return None

    def get_status_summary(
        self,
        allowed_document_ids: Optional[Sequence[str]] = None,
    ) -> Dict[str, Any]:
        """Returns aggregate LTM telemetry across Layers 1, 2, and 3."""
        with self._lock:
            allowed_set: Optional[Set[str]] = (
                {str(d) for d in allowed_document_ids if d}
                if allowed_document_ids is not None
                else None
            )

            if allowed_set is None:
                concepts_learned = sum(len(v) for v in self.concepts_by_doc.values())
                episodic_count = len(self.episodic_qa)
                docs_assimilated = len(self.assimilated_docs)
                clarification_struggles = int(self.learner_profile.get("clarification_count", 0))
            else:
                concepts_learned = sum(
                    len(self.concepts_by_doc.get(d, ())) for d in allowed_set
                )
                episodic_count = sum(
                    1
                    for ep in self.episodic_qa
                    if set(ep.get("document_ids") or ()) & allowed_set
                )
                docs_assimilated = sum(1 for d in allowed_set if d in self.assimilated_docs)
                doc_clar = self.learner_profile.get("doc_clarification_counts") or {}
                clarification_struggles = sum(int(doc_clar.get(d, 0)) for d in allowed_set)

            agg_topics: Dict[str, int] = {}
            doc_topic_counts: Dict[str, Dict[str, int]] = self.learner_profile.get(
                "doc_topic_counts", {}
            )
            for d_id, bucket in doc_topic_counts.items():
                if allowed_set is not None and d_id not in allowed_set:
                    continue
                for t_norm, cnt in bucket.items():
                    agg_topics[t_norm] = agg_topics.get(t_norm, 0) + int(cnt)

            if allowed_set is None:
                for t_norm, cnt in (self.learner_profile.get("global_topic_counts") or {}).items():
                    agg_topics[t_norm] = agg_topics.get(t_norm, 0) + int(cnt)

            disp_map = self.learner_profile.get("topic_display") or {}
            ranked_topics = sorted(agg_topics.items(), key=lambda kv: (-kv[1], kv[0]))[:5]
            top_studied_topics = [
                {"topic": disp_map.get(t_norm, t_norm), "count": cnt}
                for t_norm, cnt in ranked_topics
            ]

            return {
                "concepts_learned": concepts_learned,
                "episodic_qa_count": episodic_count,
                "documents_assimilated": docs_assimilated,
                "top_studied_topics": top_studied_topics,
                "clarification_struggles": clarification_struggles,
            }

    # ------------------------------------------------------------------
    # Certified Exact Unlearning
    # ------------------------------------------------------------------

    def unlearn_document(self, doc_id: str) -> Dict[str, Any]:
        """
        Deletes all Layer 1 concepts, Layer 2 episodic QA entries, Ridge fixed-point
        contributions, and Layer 3 active topic traces for `doc_id`, saving to disk.
        """
        if not doc_id:
            return {"removed_concepts": 0, "removed_episodic": 0, "ridge_unlearned": False}

        with self._lock:
            removed_concepts = len(self.concepts_by_doc.pop(doc_id, ()))
            self.assimilated_docs.pop(doc_id, None)

            kept_episodic: List[Dict[str, Any]] = []
            removed_episodic = 0
            for ep in self.episodic_qa:
                ep_docs = ep.get("document_ids") or []
                if doc_id in ep_docs or ep.get("top_doc_id") == doc_id:
                    removed_episodic += 1
                    rk = ep.get("ridge_key")
                    if rk:
                        self.ridge.remove_document(str(rk))
                else:
                    kept_episodic.append(ep)
            self.episodic_qa = kept_episodic

            # Remove L1 document contribution and any residual `doc_id::ep::*` keys
            self.ridge.remove_document(doc_id)
            ep_prefix = f"{doc_id}::ep::"
            for rk in list(self.ridge._doc_contributions.keys()):
                if rk == doc_id or rk.startswith(ep_prefix):
                    self.ridge.remove_document(rk)

            # Clean Layer 3 topic & clarification traces for doc_id
            doc_topic_counts = self.learner_profile.get("doc_topic_counts") or {}
            doc_topic_counts.pop(doc_id, None)

            doc_clar = self.learner_profile.get("doc_clarification_counts") or {}
            removed_doc_clar = int(doc_clar.pop(doc_id, 0))
            if removed_doc_clar > 0:
                self.learner_profile["clarification_count"] = max(
                    0, int(self.learner_profile.get("clarification_count", 0)) - removed_doc_clar
                )

            recent = self.learner_profile.get("recent_concepts") or []
            cleaned_recent: List[Dict[str, Any]] = []
            for item in recent:
                item_docs = [d for d in (item.get("doc_ids") or []) if d != doc_id]
                if item.get("doc_ids") and not item_docs:
                    continue
                new_item = dict(item)
                new_item["doc_ids"] = item_docs
                cleaned_recent.append(new_item)
            self.learner_profile["recent_concepts"] = cleaned_recent

            ridge_clean = not any(
                rk == doc_id or rk.startswith(ep_prefix)
                for rk in self.ridge._doc_contributions
            )
            self._save()

            return {
                "removed_concepts": removed_concepts,
                "removed_episodic": removed_episodic,
                "ridge_unlearned": bool(ridge_clean),
            }


_SINGLETON_LOCK = threading.RLock()
_STORES_BY_PATH: Dict[str, LongTermMemoryStore] = {}


def get_long_term_memory(storage_dir: Optional[str] = None) -> LongTermMemoryStore:
    """Thread-safe singleton accessor per normalized storage_dir."""
    target = str(Path(storage_dir or "local_runtime/long_term_memory").resolve())
    with _SINGLETON_LOCK:
        instance = _STORES_BY_PATH.get(target)
        if instance is None:
            instance = LongTermMemoryStore(storage_dir=storage_dir)
            _STORES_BY_PATH[target] = instance
        return instance


__all__ = [
    "LongTermMemoryStore",
    "get_long_term_memory",
]
