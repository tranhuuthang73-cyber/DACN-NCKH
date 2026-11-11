"""
Datasets and pattern recognition modules for Self-Study Knowledge Bank (Wave 5).
Pure-Python, strict offline.
"""

from src.self_study.datasets.cryptography_and_security_patterns import (
    expand_domain_query_terms,
    CRYPTO_SYNONYM_CLUSTERS,
    CRYPTO_FEW_SHOT_QA_EXAMPLES,
)
from src.self_study.datasets.definition_and_taxonomy_patterns import (
    extract_taxonomy_and_types,
    TAXONOMY_INSTRUCTION_DATASET,
)
from src.self_study.datasets.formula_and_example_patterns import (
    extract_examples_and_formulas,
    FORMULA_EXAMPLE_DATASET,
    is_formula_sentence,
    is_example_sentence,
    is_definition_sentence,
)
from src.self_study.datasets.question_paraphrase_normalizer import (
    normalize_student_question,
    QuestionParaphraseNormalizer,
    PARAPHRASE_DATASET,
)
from src.self_study.datasets.autonomous_qa_generator import (
    SelfCurriculumGenerator,
    CurriculumLevel,
)
from src.self_study.datasets.extractive_text_stitcher import (
    ExtractiveTextStitcher,
)

__all__ = [
    "expand_domain_query_terms",
    "CRYPTO_SYNONYM_CLUSTERS",
    "CRYPTO_FEW_SHOT_QA_EXAMPLES",
    "extract_taxonomy_and_types",
    "TAXONOMY_INSTRUCTION_DATASET",
    "extract_examples_and_formulas",
    "FORMULA_EXAMPLE_DATASET",
    "is_formula_sentence",
    "is_example_sentence",
    "is_definition_sentence",
    "normalize_student_question",
    "QuestionParaphraseNormalizer",
    "PARAPHRASE_DATASET",
    "SelfCurriculumGenerator",
    "CurriculumLevel",
    "ExtractiveTextStitcher",
]
