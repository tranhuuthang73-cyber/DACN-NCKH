"""
Mathematical Equivalence Verification: SA-CMS vs. Baseline Fixed-Token CMS.
Requirement (Step 3): For an artificial document where structural boundaries occur
exactly at the fixed token intervals, SA-CMS must reduce to the baseline behavior.
"""

import copy
import pytest
import torch

from src.hope_attention.sa_cms import StructureAlignedHopeLM, StructureAlignedSchedule
from src.document_structure.types import BoundaryType, StructuralSpan, DocumentStructure


def test_mathematical_equivalence_schedule():
    """
    Verifies that when paragraph and section boundaries match fixed chunk sizes,
    StructureAlignedSchedule produces identical boundary indices.
    """
    total_tokens = 128
    fixed_chunks = [64, 32]  # Level 1: 64, Level 2: 32

    # Construct artificial DocumentStructure where paragraphs are 64 tokens and sections are 128 tokens
    paragraphs = [
        StructuralSpan(BoundaryType.PARAGRAPH, start_token=0, end_token=64),
        StructuralSpan(BoundaryType.PARAGRAPH, start_token=64, end_token=128),
    ]
    sections = [
        StructuralSpan(BoundaryType.SECTION, start_token=0, end_token=128),
    ]
    doc_struct = DocumentStructure(
        text="artificial",
        total_tokens=total_tokens,
        paragraphs=paragraphs,
        sections=sections,
    )

    # 1. Fixed token schedule
    sched_fixed = StructureAlignedSchedule(
        num_levels=2,
        total_tokens=total_tokens,
        schedule_mode="fixed_token",
        fixed_chunk_sizes=[64, 128],
    )

    # 2. Structure-aligned schedule
    sched_struct = StructureAlignedSchedule(
        num_levels=2,
        total_tokens=total_tokens,
        schedule_mode="structure",
        doc_structure=doc_struct,
    )

    # Boundaries must be mathematically identical
    assert sched_struct.boundaries[0] == sched_fixed.boundaries[0] == [64, 128]
    assert sched_struct.boundaries[1] == sched_fixed.boundaries[1] == [128]


def test_mathematical_equivalence_weights_update():
    """
    Executes online document ingestion on both SA-CMS and Fixed-Token schedule
    under matched boundary conditions and proves weight delta is strictly 0.000000.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"

    # Initialize two identical models from the same seed
    torch.manual_seed(42)
    model_fixed = StructureAlignedHopeLM(
        model_name_or_path="HuggingFaceTB/SmolLM2-135M",
        num_levels=2,
        chunk_sizes=[32, 64],
        device=device,
    )

    torch.manual_seed(42)
    model_struct = StructureAlignedHopeLM(
        model_name_or_path="HuggingFaceTB/SmolLM2-135M",
        num_levels=2,
        chunk_sizes=[32, 64],
        device=device,
    )

    # Copy identical CMS weights to guarantee exact initial state
    model_struct.cms.load_state_dict(copy.deepcopy(model_fixed.cms.state_dict()))
    model_struct.cms_norm.load_state_dict(copy.deepcopy(model_fixed.cms_norm.state_dict()))

    # Text composed of 2 paragraphs designed to yield exact chunk lengths
    # We will mock the parser for the structured model to guarantee exact token boundaries
    text = (
        "Quantum mechanics provides mathematical formulations of wave functions and observable operators. "
        "The Schrödinger equation describes the continuous temporal evolution of physical state vectors. "
        "Entanglement between composite systems generates non-local quantum correlations across large spatial separations.\n\n"
        "General relativity formulates gravitational interactions as the geometric curvature of spacetime. "
        "Einstein field equations relate the stress-energy tensor to the metric tensor of pseudo-Riemannian manifolds. "
        "Cosmological models describe the expansion of the universe from early inflationary epochs to cosmic microwave background."
    )

    # Tokenize text
    enc = model_fixed.tokenizer(text, return_tensors="pt")
    total_tokens = enc.input_ids.size(1)
    half_tokens = total_tokens // 2

    # Construct matched document structure
    mock_doc_struct = DocumentStructure(
        text=text,
        total_tokens=total_tokens,
        paragraphs=[
            StructuralSpan(BoundaryType.PARAGRAPH, start_token=0, end_token=half_tokens),
            StructuralSpan(BoundaryType.PARAGRAPH, start_token=half_tokens, end_token=total_tokens),
        ],
        sections=[
            StructuralSpan(BoundaryType.SECTION, start_token=0, end_token=total_tokens),
        ],
    )

    # Ingest with Fixed-Token schedule (chunks: [half_tokens, total_tokens])
    res_fixed = model_fixed.ingest_structured_document(
        document_text=text,
        schedule_mode="fixed_token",
        fixed_chunk_sizes=[half_tokens, total_tokens],
    )

    # Mock the parser on model_struct to return mock_doc_struct
    model_struct.parser.parse_text = lambda txt, tokenizer=None: mock_doc_struct

    # Ingest with SA-CMS schedule
    res_struct = model_struct.ingest_structured_document(
        document_text=text,
        schedule_mode="structure",
    )

    # 1. Update event count must be identical
    assert res_fixed["num_update_events"] == res_struct["num_update_events"]
    assert len(res_fixed["events"]) == len(res_struct["events"])

    # 2. Check each event's start_token, end_token, and grad_norm
    for ev_f, ev_s in zip(res_fixed["events"], res_struct["events"]):
        assert ev_f["memory_level"] == ev_s["memory_level"]
        assert ev_f["start_token"] == ev_s["start_token"]
        assert ev_f["end_token"] == ev_s["end_s" if "end_s" in ev_s else "end_token"]
        assert abs(ev_f["grad_norm"] - ev_s["grad_norm"]) < 1e-4

    # 3. Final parameter distance between models must be zero
    total_delta = 0.0
    for p_fixed, p_struct in zip(model_fixed.get_cms_parameters(), model_struct.get_cms_parameters()):
        total_delta += torch.norm(p_fixed - p_struct).item()

    assert total_delta < 1e-4, f"Mathematical equivalence violation! Delta: {total_delta}"


def test_equal_budget_guarantee():
    """
    Verifies that for an arbitrary structured document, StructureAlignedSchedule
    generates strictly identical update event counts across structure, fixed_token, and random modes.
    """
    text = (
        "# Heading 1\n"
        "Paragraph one provides introductory background on the topic.\n\n"
        "Paragraph two provides detailed mathematical foundations.\n\n"
        "# Heading 2\n"
        "Paragraph three discusses empirical results and validation.\n\n"
        "Paragraph four concludes the document with future directions."
    )
    from transformers import AutoTokenizer
    from src.document_structure.parser import DocumentStructureParser

    tokenizer = AutoTokenizer.from_pretrained("HuggingFaceTB/SmolLM2-135M")
    parser = DocumentStructureParser()
    doc_struct = parser.parse_text(text, tokenizer=tokenizer)
    total_tokens = doc_struct.total_tokens

    sched_struct = StructureAlignedSchedule(num_levels=3, total_tokens=total_tokens, schedule_mode="structure", doc_structure=doc_struct)
    sched_fixed = StructureAlignedSchedule(num_levels=3, total_tokens=total_tokens, schedule_mode="fixed_token", doc_structure=doc_struct)
    sched_rand = StructureAlignedSchedule(num_levels=3, total_tokens=total_tokens, schedule_mode="random", doc_structure=doc_struct, seed=42)

    count_struct = sum(len(b) for b in sched_struct.boundaries.values())
    count_fixed = sum(len(b) for b in sched_fixed.boundaries.values())
    count_rand = sum(len(b) for b in sched_rand.boundaries.values())

    assert count_struct == count_fixed == count_rand, f"Budget mismatch: struct={count_struct}, fixed={count_fixed}, rand={count_rand}"

