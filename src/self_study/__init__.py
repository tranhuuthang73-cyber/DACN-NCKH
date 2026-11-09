"""
Self-Study & Neural Reader Module (Sections 6.4 and 6.5 of Research Proposal).
100% Strict Offline, Zero External API, Local PyTorch & Rule-Based Operations.
"""

from src.self_study.types import (
    QARuleType,
    SelfStudyQAPair,
    SelfStudyReport,
)
from src.self_study.extractor import QAPairExtractor

__all__ = [
    "QARuleType",
    "SelfStudyQAPair",
    "SelfStudyReport",
    "QAPairExtractor",
]
