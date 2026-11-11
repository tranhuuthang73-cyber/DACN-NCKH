"""
Neural Query Decomposer: Decomposes compound, multi-part, or comparative queries
into atomic sub-queries for multi-hop retrieval and synthesis.
"""

from dataclasses import dataclass, field
from typing import List, Optional
import re


@dataclass
class SubQuery:
    text: str
    intent: str = "general"
    dependency_index: Optional[int] = None


@dataclass
class DecompositionResult:
    is_compound: bool
    sub_queries: List[SubQuery] = field(default_factory=list)
    original_query: str = ""


class QueryDecomposer:
    """
    Decomposes complex user queries into atomic sub-questions.
    Follows Ponytail principles: deterministic, fast regex heuristics with zero heavy LLM overhead.
    """

    COMPARISON_PATTERNS = [
        re.compile(r"so sánh\s+(?:sự khác biệt giữa|điểm khác biệt giữa|giữa)?\s*([^,\.]+?)\s+và\s+([^,\.\?]+)", re.IGNORECASE),
        re.compile(r"sự khác (?:nhau|biệt) giữa\s+([^,\.]+?)\s+và\s+([^,\.\?]+)", re.IGNORECASE),
    ]

    CONJUNCTION_SPLITTERS = [
        r"\s+đồng thời\s+",
        r"\s+song song đó\s+",
        r"\s+cũng như\s+",
        r"\s+ngoài ra\s+",
        r"\s+và\s+",
    ]

    def decompose(self, query: str) -> DecompositionResult:
        q_clean = query.strip()
        if not q_clean:
            return DecompositionResult(is_compound=False, sub_queries=[SubQuery(query)], original_query=query)

        # 1. Comparison query pattern
        for pat in self.COMPARISON_PATTERNS:
            m = pat.search(q_clean)
            if m:
                ent_a = m.group(1).strip()
                ent_b = m.group(2).strip()
                sub_queries = [
                    SubQuery(text=f"Đặc điểm và nội dung của {ent_a} là gì?", intent="comparison_a"),
                    SubQuery(text=f"Đặc điểm và nội dung của {ent_b} là gì?", intent="comparison_b"),
                ]
                return DecompositionResult(
                    is_compound=True,
                    sub_queries=sub_queries,
                    original_query=query,
                )

        # 2. Sequential question mark split: "Câu hỏi 1? Câu hỏi 2?"
        if "?" in q_clean[:-1]:
            parts = [p.strip() for p in q_clean.split("?") if len(p.strip()) >= 10]
            if len(parts) >= 2:
                sub_queries = [
                    SubQuery(text=f"{p}?" if not p.endswith("?") else p, intent="sequential")
                    for p in parts
                ]
                return DecompositionResult(
                    is_compound=True,
                    sub_queries=sub_queries,
                    original_query=query,
                )

        # 3. Conjunction splitting
        for pattern in self.CONJUNCTION_SPLITTERS:
            if re.search(pattern, q_clean, re.IGNORECASE):
                parts = re.split(pattern, q_clean, flags=re.IGNORECASE)
                parts = [p.strip() for p in parts if len(p.strip()) >= 10]
                if len(parts) >= 2:
                    # Enrich second clause if missing interrogative structure
                    sub_queries = []
                    for idx, part in enumerate(parts):
                        txt = part.rstrip("?. ")
                        if not any(k in txt.lower() for k in ["là gì", "thế nào", "ra sao", "bao nhiêu", "ai", "ở đâu"]):
                            txt = f"Nội dung về {txt} là gì?"
                        else:
                            txt = f"{txt}?"
                        sub_queries.append(SubQuery(text=txt, intent=f"part_{idx+1}"))

                    return DecompositionResult(
                        is_compound=True,
                        sub_queries=sub_queries,
                        original_query=query,
                    )

        # Single atomic query fallback
        return DecompositionResult(
            is_compound=False,
            sub_queries=[SubQuery(text=query, intent="atomic")],
            original_query=query,
        )
