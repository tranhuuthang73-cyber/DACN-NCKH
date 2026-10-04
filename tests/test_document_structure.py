"""
Unit tests for DocumentStructureParser and multi-level structural hierarchy.
"""

import pytest
from src.document_structure.types import BoundaryType, StructuralSpan, DocumentStructure
from src.document_structure.parser import DocumentStructureParser


@pytest.fixture
def parser():
    return DocumentStructureParser(
        fallback_paragraph_tokens=16,
        fallback_section_tokens=32,
        paragraphs_per_section_fallback=2,
    )


def test_paragraph_detection(parser):
    text = (
        "This is paragraph one about astrophysics and black holes.\n\n"
        "This is paragraph two describing quantum gravity and entanglement.\n\n"
        "This is paragraph three summarizing future experimental probes."
    )
    doc_struct = parser.parse_text(text)
    assert len(doc_struct.paragraphs) == 3
    for p in doc_struct.paragraphs:
        assert p.span_type == BoundaryType.PARAGRAPH
        assert p.token_length > 0
    assert doc_struct.paragraphs[0].start_token == 0
    assert doc_struct.paragraphs[-1].end_token == doc_struct.total_tokens


def test_section_detection_markdown(parser):
    text = (
        "# Introduction\n"
        "We introduce the nested learning paradigm and continuous memory systems.\n\n"
        "# Methodology\n"
        "Here we define multi-level optimization and structure-aligned scheduling.\n\n"
        "# Experiments\n"
        "Empirical results on document QA and multi-key retrieval."
    )
    doc_struct = parser.parse_text(text)
    assert doc_struct.metadata["has_real_sections"] is True
    assert len(doc_struct.sections) == 3
    titles = [s.title for s in doc_struct.sections]
    assert any("Introduction" in t for t in titles)
    assert any("Methodology" in t for t in titles)
    assert any("Experiments" in t for t in titles)


def test_section_detection_numbered(parser):
    text = (
        "1. Overview\n"
        "Deep learning models compress their context flow.\n\n"
        "2. Architecture\n"
        "Continuum memory systems adapt parameters online."
    )
    doc_struct = parser.parse_text(text)
    assert doc_struct.metadata["has_real_sections"] is True
    assert len(doc_struct.sections) == 2


def test_document_boundaries(parser):
    text = "Short single paragraph document."
    doc_struct = parser.parse_text(text)
    assert doc_struct.document_span is not None
    assert doc_struct.document_span.span_type == BoundaryType.DOCUMENT
    assert doc_struct.document_span.start_token == 0
    assert doc_struct.document_span.end_token == doc_struct.total_tokens


def test_fallback_behavior_no_headings(parser):
    text = (
        "First narrative paragraph with some detailed facts.\n\n"
        "Second narrative paragraph expanding on the previous statement.\n\n"
        "Third narrative paragraph continuing the discussion.\n\n"
        "Fourth narrative paragraph concluding the story."
    )
    doc_struct = parser.parse_text(text)
    assert doc_struct.metadata["has_real_sections"] is False
    # Should fall back to paragraph clustering
    assert len(doc_struct.sections) >= 2
    assert doc_struct.sections[0].metadata.get("fallback") == "paragraph_cluster"


def test_fallback_behavior_unstructured_continuous_text(parser):
    text = "A single massive continuous sentence without any linebreaks or punctuation headers at all."
    doc_struct = parser.parse_text(text)
    assert len(doc_struct.paragraphs) >= 1
    assert len(doc_struct.sections) >= 1
    assert doc_struct.total_tokens > 0


def test_get_update_boundaries(parser):
    text = (
        "# Sec 1\n"
        "P1 text here.\n\n"
        "P2 text here.\n\n"
        "# Sec 2\n"
        "P3 text here."
    )
    doc_struct = parser.parse_text(text)
    p_bounds = doc_struct.get_update_boundaries(level=1)
    s_bounds = doc_struct.get_update_boundaries(level=2)
    d_bounds = doc_struct.get_update_boundaries(level=3)

    assert len(p_bounds) >= len(s_bounds)
    assert len(s_bounds) >= len(d_bounds)
    assert d_bounds[-1] == doc_struct.total_tokens


def test_random_boundary_generation():
    total_tokens = 100
    num_bounds = 5
    bounds = DocumentStructureParser.generate_random_boundaries(total_tokens, num_bounds, seed=42)
    assert len(bounds) == num_bounds
    assert bounds[-1] == total_tokens
    assert bounds == sorted(bounds)
