"""
Refusal Controller — decides whether to answer or refuse based on evidence.

Per the research proposal:
    - If documents do not contain supporting information → refuse.
    - Distinguish between "retriever found nothing" and "document definitely
      does not contain the information".
    - Threshold/policy is configurable.

Two outcomes:
    1. ANSWER + CITATION (has evidence)
    2. REFUSAL (insufficient evidence)
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional
from enum import Enum

from src.hybrid_qa.evidence import EvidencePackage


class DecisionType(Enum):
    ANSWER = "answer"
    REFUSAL = "refusal"


class RefusalReason(Enum):
    NO_EVIDENCE = "no_relevant_evidence_found"
    LOW_CONFIDENCE = "evidence_below_confidence_threshold"
    INSUFFICIENT_COVERAGE = "insufficient_evidence_coverage"


@dataclass
class RefusalDecision:
    """Decision about whether to answer or refuse."""
    decision: DecisionType
    reason: Optional[RefusalReason] = None
    confidence: float = 0.0
    refusal_message: str = ""
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    @property
    def should_answer(self) -> bool:
        return self.decision == DecisionType.ANSWER

    @property
    def should_refuse(self) -> bool:
        return self.decision == DecisionType.REFUSAL

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.decision.value,
            "reason": self.reason.value if self.reason else None,
            "confidence": self.confidence,
            "refusal_message": self.refusal_message,
            "metadata": self.metadata,
        }


class RefusalController:
    """
    Configurable refusal policy based on evidence quality.
    
    Parameters:
    - min_evidence_score: minimum max evidence score to accept.
    - min_evidence_count: minimum number of evidence passages.
    - no_evidence_message: refusal text when no evidence.
    - low_confidence_message: refusal text when evidence is weak.
    """

    DEFAULT_NO_EVIDENCE_MSG = (
        "The provided documents do not contain information relevant to this question."
    )
    DEFAULT_LOW_CONFIDENCE_MSG = (
        "The available evidence is insufficient to provide a reliable answer."
    )
    DEFAULT_INSUFFICIENT_COVERAGE_MSG = (
        "The available evidence does not sufficiently cover the question."
    )

    VIETNAMESE_NO_EVIDENCE_MSG = (
        "Tài liệu được cung cấp không chứa thông tin liên quan đến câu hỏi này."
    )
    VIETNAMESE_LOW_CONFIDENCE_MSG = (
        "Bằng chứng hiện có không đủ để đưa ra câu trả lời tin cậy."
    )
    VIETNAMESE_INSUFFICIENT_COVERAGE_MSG = (
        "Bằng chứng tìm thấy chưa bao quát đầy đủ nội dung câu hỏi."
    )

    def __init__(
        self,
        min_evidence_score: float = 1.0,
        min_evidence_count: int = 1,
        min_query_coverage: float = 0.0,
        no_evidence_message: Optional[str] = None,
        low_confidence_message: Optional[str] = None,
    ):
        self.min_evidence_score = min_evidence_score
        self.min_evidence_count = min_evidence_count
        self.min_query_coverage = min_query_coverage
        self.no_evidence_message = no_evidence_message or self.DEFAULT_NO_EVIDENCE_MSG
        self.low_confidence_message = low_confidence_message or self.DEFAULT_LOW_CONFIDENCE_MSG

    @staticmethod
    def _is_vietnamese(text: str) -> bool:
        if not text:
            return False
        vi_chars = set("àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ"
                       "ÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ")
        return any(c in vi_chars for c in text)

    def decide(self, evidence: EvidencePackage, language: Optional[str] = None) -> RefusalDecision:
        """
        Decide whether to answer or refuse based on evidence quality.
        
        Logic:
        1. No evidence passages → REFUSE (no evidence)
        2. Max score below threshold → REFUSE (low confidence)
        3. Count below minimum or query coverage below threshold → REFUSE (insufficient coverage)
        4. Otherwise → ANSWER
        """
        n_evidence = len(evidence.evidence_passages)
        max_score = evidence.max_evidence_score
        cov = getattr(evidence, "query_coverage", 1.0)

        # Detect language for appropriate refusal message
        is_vi = language in ("vi", "vietnamese") if language else self._is_vietnamese(evidence.query)

        no_ev_msg = self.VIETNAMESE_NO_EVIDENCE_MSG if is_vi else self.no_evidence_message
        low_conf_msg = self.VIETNAMESE_LOW_CONFIDENCE_MSG if is_vi else self.low_confidence_message
        insuff_cov_msg = self.VIETNAMESE_INSUFFICIENT_COVERAGE_MSG if is_vi else (
            self.low_confidence_message or self.DEFAULT_INSUFFICIENT_COVERAGE_MSG
        )

        # Case 1: No evidence at all
        if n_evidence == 0:
            return RefusalDecision(
                decision=DecisionType.REFUSAL,
                reason=RefusalReason.NO_EVIDENCE,
                confidence=0.0,
                refusal_message=no_ev_msg,
                metadata={
                    "total_passages_searched": evidence.total_passages_searched,
                    "evidence_count": 0,
                    "language": "vi" if is_vi else "en",
                },
            )

        # Case 2: Evidence too weak
        if max_score < self.min_evidence_score:
            return RefusalDecision(
                decision=DecisionType.REFUSAL,
                reason=RefusalReason.LOW_CONFIDENCE,
                confidence=max_score / max(self.min_evidence_score, 1e-6),
                refusal_message=low_conf_msg,
                metadata={
                    "max_score": max_score,
                    "threshold": self.min_evidence_score,
                    "evidence_count": n_evidence,
                    "language": "vi" if is_vi else "en",
                },
            )

        # Case 3: Insufficient coverage (either passage count or query term coverage)
        if n_evidence < self.min_evidence_count or cov < self.min_query_coverage or not evidence.has_sufficient_evidence:
            return RefusalDecision(
                decision=DecisionType.REFUSAL,
                reason=RefusalReason.INSUFFICIENT_COVERAGE,
                confidence=cov,
                refusal_message=insuff_cov_msg,
                metadata={
                    "evidence_count": n_evidence,
                    "min_required": self.min_evidence_count,
                    "query_coverage": cov,
                    "min_query_coverage": self.min_query_coverage,
                    "language": "vi" if is_vi else "en",
                },
            )

        # Case 4: Sufficient evidence → answer
        confidence = min(1.0, max_score / max(self.min_evidence_score, 1e-6))
        return RefusalDecision(
            decision=DecisionType.ANSWER,
            confidence=confidence,
            metadata={
                "evidence_count": n_evidence,
                "max_score": max_score,
                "query_coverage": cov,
                "language": "vi" if is_vi else "en",
            },
        )
