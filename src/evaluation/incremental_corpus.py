"""
Incremental Sequential Document Ingestion Corpus for RQ4 Catastrophic Forgetting.
Conforms to De cuong NCKH Section 7.1 and Phase 4.0.3 scope lock:
- Initial document D0 with 10 diagnostic ground-truth QA pairs.
- Stream of 20 sequential domain-diverse documents (D1 to D20).
- Evaluation intervals: D0 (checkpoint +0), +5 docs, +10 docs, +20 docs.
- Measures retention accuracy and forgetting delta on the identical D0 questions.
"""

from typing import Dict, Any, List, Tuple


def get_incremental_corpus() -> Dict[str, Any]:
    """Returns D0 document with 10 QA pairs, and 20 sequential stream documents."""
    
    d0_doc = {
        "doc_id": "INC_DOC_000",
        "title": "Quantum Memory Registers in Multi-Timescale Optical Lattices",
        "text": (
            "## 1. Physical Principle and Architecture\n"
            "Quantum memory registers utilize cold rubidium-87 atomic ensembles trapped within a 3D optical lattice. "
            "Coherent optical storage is mediated via electromagnetically induced transparency (EIT) with a control laser "
            "tuned to the 795 nm D1 transition. The primary storage coherence time is measured at 125 milliseconds.\n\n"
            "## 2. Multi-Level State Storage\n"
            "The memory architecture operates across three quantum spin levels. Level 1 stores hyperfine ground states "
            "with a fidelity of 96.8%. Level 2 preserves Zeeman sublevels with a write latency of 45 nanoseconds. "
            "Level 3 mediates optical cavity coupling with a photon retrieval efficiency of 82.4%.\n\n"
            "## 3. Error Mitigation and Consolidation\n"
            "Dynamic decoupling pulses applied at 10 microsecond intervals mitigate magnetic field fluctuations. "
            "Under cryogenic cooling to 4.2 Kelvin, phase decoherence is reduced by 74% compared to room temperature. "
            "The system sustains 10,000 read-write cycles before requiring repumping."
        ),
        "questions": [
            {
                "q_id": "D0_Q01",
                "question": "What atomic isotope is trapped within the optical lattice?",
                "ground_truth": "rubidium-87",
                "keywords": ["rubidium-87", "rubidium", "87"]
            },
            {
                "q_id": "D0_Q02",
                "question": "What is the primary storage coherence time of the quantum register?",
                "ground_truth": "125 milliseconds",
                "keywords": ["125", "milliseconds", "125 ms"]
            },
            {
                "q_id": "D0_Q03",
                "question": "What physical mechanism mediates coherent optical storage?",
                "ground_truth": "electromagnetically induced transparency (EIT)",
                "keywords": ["electromagnetically induced transparency", "eit"]
            },
            {
                "q_id": "D0_Q04",
                "question": "What wavelength is the control laser tuned to for the D1 transition?",
                "ground_truth": "795 nm",
                "keywords": ["795", "nm", "795 nm"]
            },
            {
                "q_id": "D0_Q05",
                "question": "What is the storage fidelity of Level 1 hyperfine ground states?",
                "ground_truth": "96.8%",
                "keywords": ["96.8%", "96.8"]
            },
            {
                "q_id": "D0_Q06",
                "question": "What is the write latency for preserving Zeeman sublevels in Level 2?",
                "ground_truth": "45 nanoseconds",
                "keywords": ["45", "nanoseconds", "45 ns"]
            },
            {
                "q_id": "D0_Q07",
                "question": "What photon retrieval efficiency is achieved by Level 3 optical cavity coupling?",
                "ground_truth": "82.4%",
                "keywords": ["82.4%", "82.4"]
            },
            {
                "q_id": "D0_Q08",
                "question": "What interval is utilized for dynamic decoupling pulses?",
                "ground_truth": "10 microsecond intervals",
                "keywords": ["10", "microsecond", "10 microsecond"]
            },
            {
                "q_id": "D0_Q09",
                "question": "To what cryogenic temperature is the register cooled?",
                "ground_truth": "4.2 Kelvin",
                "keywords": ["4.2", "kelvin", "4.2 k"]
            },
            {
                "q_id": "D0_Q10",
                "question": "How many read-write cycles can the system sustain before repumping?",
                "ground_truth": "10,000 cycles",
                "keywords": ["10,000", "10000", "cycles"]
            }
        ]
    }

    # 20 sequential stream documents covering diverse domains
    stream_topics = [
        ("INC_DOC_001", "Gravitational Wave Interferometry and Advanced LIGO Detectors", "Physics"),
        ("INC_DOC_002", "CRISPR-Cas9 Base Editing in Hematopoietic Stem Cells", "Genetics"),
        ("INC_DOC_003", "Autonomous Electric Flight and Lithium-Sulfur Batteries", "Aerospace"),
        ("INC_DOC_004", "Transformer Scaling Laws and Mixture-of-Experts Routing", "AI"),
        ("INC_DOC_005", "Deep Sea Hydrothermal Vent Microbial Ecology", "Marine Biology"),
        ("INC_DOC_006", "Solid-State Electrolyte Interfaces in Sodium-Ion Cells", "Materials Science"),
        ("INC_DOC_007", "Neuromorphic Spike Timing Dependent Plasticity Chips", "Neuroscience"),
        ("INC_DOC_008", "Global Trade Policy and Supply Chain Deglobalization", "Economics"),
        ("INC_DOC_009", "Photonic Crystal Fibers for Mid-Infrared Laser Delivery", "Optics"),
        ("INC_DOC_010", "Synthetic Biology Metabolic Engineering of Artemisinin", "Biotechnology"),
        ("INC_DOC_011", "Exoplanet Atmospheric Spectroscopy via James Webb Space Telescope", "Astronomy"),
        ("INC_DOC_012", "Post-Quantum Cryptography Lattice Signatures and Falcon-512", "Cryptography"),
        ("INC_DOC_013", "Perovskite-Silicon Tandem Solar Cell Degradation Kinetics", "Clean Energy"),
        ("INC_DOC_014", "Deep Brain Stimulation Closed-Loop Systems in Parkinsonism", "Medicine"),
        ("INC_DOC_015", "Distributed Byzantine Fault Tolerant Consensus Protocols", "Distributed Systems"),
        ("INC_DOC_016", "Carbon Nanotube Field Effect Transistors at 1nm Gate Length", "Nanotechnology"),
        ("INC_DOC_017", "Oceanic Thermohaline Circulation Changes and AMOC Stability", "Climate Science"),
        ("INC_DOC_018", "Protein Folding Allosteric Pathway Prediction using Equivariant GNNs", "Structural Biology"),
        ("INC_DOC_019", "Autonomous Underwater Glider Swarm Acoustic Telemetry", "Robotics"),
        ("INC_DOC_020", "Nuclear Fusion Tokamak Plasma Stability and Magnetic Confinement", "Plasma Physics")
    ]

    stream_docs = []
    for doc_id, title, field in stream_topics:
        doc_text = (
            f"## 1. Overview of {title}\n"
            f"Research in the discipline of {field} addresses fundamental questions of mechanism and design. "
            f"Recent technical literature emphasizes reproducible standardized benchmarks and quantitative validation protocols.\n\n"
            f"## 2. Experimental Observations\n"
            f"Data collected across multi-stage testing facilities demonstrates measurable improvements in efficiency, "
            f"corroborating earlier theoretical predictions with a statistical confidence level exceeding 99%.\n\n"
            f"## 3. Systematic Integration\n"
            f"Deploying integrated frameworks across large-scale facilities requires coordinated timing, robust telemetry, "
            f"and strict error monitoring to prevent divergence during continuous operations."
        )
        stream_docs.append({
            "doc_id": doc_id,
            "title": title,
            "field": field,
            "text": doc_text
        })

    return {
        "d0_document": d0_doc,
        "stream_documents": stream_docs
    }
