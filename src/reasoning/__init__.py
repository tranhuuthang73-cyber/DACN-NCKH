"""
Neuro-Symbolic Reasoning Module for SA-CMS.
Implements Concept Hypergraph, Multi-Hop Path Reasoning, and Cross-Document Contradiction Detection.
100% Strict Offline, Local Pure Python & PyTorch Data Structures.
"""

from src.reasoning.hypergraph import (
    RelationType,
    ConceptNode,
    RelationEdge,
    MultiHopChain,
    ConceptHypergraph,
)
from src.reasoning.cross_doc_scanner import (
    ContradictionType,
    ContradictionAlert,
    ContradictionScanReport,
    CrossDocumentContradictionScanner,
)

__all__ = [
    "RelationType",
    "ConceptNode",
    "RelationEdge",
    "MultiHopChain",
    "ConceptHypergraph",
    "ContradictionType",
    "ContradictionAlert",
    "ContradictionScanReport",
    "CrossDocumentContradictionScanner",
]
