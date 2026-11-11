"""
Reflective Grounding Critic: Verifies answers against retrieved citations
to eliminate hallucinations, over-extrapolations, and unsupported numerical claims.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import re


@dataclass
class ClaimVerificationResult:
    claim_text: str
    is_supported: bool
    supporting_citation_index: Optional[int] = None
    overlap_score: float = 0.0
    unsupported_entities: List[str] = field(default_factory=list)


@dataclass
class CriticReport:
    is_faithful: bool
    faithfulness_score: float
    claims: List[ClaimVerificationResult] = field(default_factory=list)
    unsupported_claims: List[str] = field(default_factory=list)


class GroundingCritic:
    """
    Reflective Critic that validates generated claims against source citations.
    Follows Ponytail principles: pure deterministic verification without invoking external LLMs.
    """

    NUMERIC_ENTITY_PATTERN = re.compile(r"\b\d+(?:[.,]\d+)?\s*(?:%|phần trăm|triệu|tỷ|token[s]?|ms|s|gb|mb|năm)?\b", re.IGNORECASE)

    def verify_answer(self, answer: str, citations: List[Dict[str, Any]]) -> CriticReport:
        if not citations:
            return CriticReport(is_faithful=False, faithfulness_score=0.0, unsupported_claims=[answer])

        # Aggregate citation text for fast verification
        all_citation_text = " ".join(c.get("text", "") for c in citations).lower()
        citation_tokens = set(re.findall(r"\w+", all_citation_text))

        # Filter out meta-headers and sources from claims
        clean_text = answer
        for header in ["### Nguồn tham khảo", "💡 **Câu hỏi tự học tiếp theo:**", "🧠 **Tiến trình nơ-ron"]:
            if header in clean_text:
                clean_text = clean_text.split(header)[0]

        sentences = [
            s.strip() for s in re.split(r"(?<=[.!?])\s+|\n+", clean_text)
            if len(s.strip()) >= 15 and not s.strip().startswith(("#", "-", "*", "🧠", "💡"))
        ]

        if not sentences:
            return CriticReport(is_faithful=True, faithfulness_score=1.0)

        claims_res: List[ClaimVerificationResult] = []
        unsupported: List[str] = []

        for sentence in sentences:
            s_low = sentence.lower()
            s_tokens = set(re.findall(r"\w+", s_low))
            if not s_tokens:
                continue

            # 1. Check numbers/metrics
            numbers_in_sentence = self.NUMERIC_ENTITY_PATTERN.findall(sentence)
            unsupported_nums = [
                n.strip() for n in numbers_in_sentence
                if n.strip().lower() not in all_citation_text
            ]

            # 2. Token overlap score
            overlap_count = len(s_tokens.intersection(citation_tokens))
            overlap_score = overlap_count / max(1, len(s_tokens))

            # Supported if reasonable token overlap AND no hallucinated numbers
            is_supported = (overlap_score >= 0.30) and (len(unsupported_nums) == 0)

            if not is_supported:
                unsupported.append(sentence)

            claims_res.append(
                ClaimVerificationResult(
                    claim_text=sentence,
                    is_supported=is_supported,
                    overlap_score=overlap_score,
                    unsupported_entities=unsupported_nums,
                )
            )

        supported_count = sum(1 for c in claims_res if c.is_supported)
        score = supported_count / max(1, len(claims_res))
        is_faithful = (score >= 0.70) and (len(unsupported) == 0)

        return CriticReport(
            is_faithful=is_faithful,
            faithfulness_score=score,
            claims=claims_res,
            unsupported_claims=unsupported,
        )

    def correct_answer(self, answer: str, report: CriticReport) -> str:
        """
        Reflectively corrects an answer by appending an explicit boundary advisory
        or pruning unsubstantiated claims.
        """
        if report.is_faithful or not report.unsupported_claims:
            return answer

        # If answer contains hallucinated metrics, append an advisory warning
        advisories = []
        for claim in report.claims:
            if not claim.is_supported and claim.unsupported_entities:
                advisories.append(
                    f"*(Lưu ý đối soát: Chi tiết '{', '.join(claim.unsupported_entities)}' không có trong tài liệu đối chiếu)*"
                )

        if advisories:
            return f"{answer}\n\n" + "\n".join(advisories)

        return f"{answer}\n\n*(Lưu ý đối soát: Một số nhận định trên không có trong tài liệu trực tiếp)*"

