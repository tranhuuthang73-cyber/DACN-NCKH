"""
Manual Single-Sample Diagnostic & Validation for Track 2 Pretrained MK-NIAH.
Verifies SmolLM2-135M with Natural MK-NIAH before running full baseline ablations.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import torch

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.hope_attention.pretrained_hope import PretrainedHopeLM
from src.evaluation.pretrained_benchmarks import NaturalMKNIAHBenchmark
from src.utils.logger import setup_logger


def debug_pretrained_sample():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = str(ROOT_DIR / "logs")
    filename = f"debug_pretrained_mkniah_{timestamp}.log"
    logger = setup_logger("DebugPretrainedMKNIAH", log_dir=log_dir, filename=filename)

    logger.info("=" * 80)
    logger.info("STARTING TRACK 2 MK-NIAH MANUAL SAMPLE VALIDATION (TASK 8)")
    logger.info("=" * 80)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Using compute device: {device}")

    # Generate 1 sample
    bench = NaturalMKNIAHBenchmark(num_samples=1, num_keys=3, seed=42)
    sample = bench._generate_sample(0)

    logger.info("\n--- SAMPLE DETAILS ---")
    logger.info(f"Queried Key: {sample['queried_key']}")
    logger.info(f"Expected Answer: {sample['expected_val']}")
    logger.info(f"All Embedded Needles: {sample['needles']}")
    logger.info(f"Prompt Text (truncated to 200 chars):\n'{sample['prompt_text'][:200]}...'")
    logger.info(f"Prompt Tail:\n'...{sample['prompt_text'][-150:]}'")

    # 1. Test Baseline ICL (Level 1 - pure SmolLM2-135M)
    logger.info("\n" + "=" * 50)
    logger.info("1. EVALUATING LEVEL 1 (ICL BASELINE - PURE PRETRAINED BACKBONE)")
    logger.info("=" * 50)

    model_icl = PretrainedHopeLM(
        model_name_or_path="HuggingFaceTB/SmolLM2-135M",
        num_levels=1,
        device=device,
    )
    vram_icl = torch.cuda.memory_allocated() / (1024 ** 2)
    logger.info(f"Model Level 1 loaded. VRAM allocated: {vram_icl:.2f} MB")

    res_icl = bench.evaluate_model(model_icl, enable_online_cms=False, logger=logger)
    sample_res_icl = res_icl["detailed_samples"][0]

    logger.info("\n[LEVEL 1 ICL RESULTS]")
    logger.info(f"Expected Answer: {sample_res_icl['expected_val']}")
    logger.info(f"Model First Pred Token: '{sample_res_icl['first_pred_token']}'")
    logger.info(f"Model Generated Answer: '{sample_res_icl['generated_answer']}'")
    logger.info(f"Target Token Probability: {sample_res_icl['target_prob']:.6f}")
    logger.info(f"Target Rank in Vocab: {sample_res_icl['target_rank']} / {model_icl.vocab_size}")
    logger.info(f"Top 5 Predicted Tokens: {sample_res_icl['top5_tokens']}")
    logger.info(f"Top 5 Probabilities: {sample_res_icl['top5_probs']}")
    logger.info(f"Evaluator Exact Match: {sample_res_icl['is_correct']}")

    # 2. Test Level 2 CMS
    logger.info("\n" + "=" * 50)
    logger.info("2. EVALUATING LEVEL 2 (CMS MEMORY ADAPTATION - EQUATION 71)")
    logger.info("=" * 50)

    model_cms = PretrainedHopeLM(
        model_name_or_path="HuggingFaceTB/SmolLM2-135M",
        num_levels=2,
        chunk_sizes=[64, 32],
        device=device,
    )
    cms_params = sum(p.numel() for p in model_cms.get_cms_parameters())
    vram_cms = torch.cuda.memory_allocated() / (1024 ** 2)
    logger.info(f"Model Level 2 loaded. Trainable CMS Params: {cms_params:,}, VRAM: {vram_cms:.2f} MB")

    res_cms = bench.evaluate_model(model_cms, enable_online_cms=True, logger=logger)
    sample_res_cms = res_cms["detailed_samples"][0]

    logger.info("\n[LEVEL 2 CMS RESULTS]")
    logger.info(f"Expected Answer: {sample_res_cms['expected_val']}")
    logger.info(f"Model First Pred Token: '{sample_res_cms['first_pred_token']}'")
    logger.info(f"Model Generated Answer: '{sample_res_cms['generated_answer']}'")
    logger.info(f"Target Token Probability: {sample_res_cms['target_prob']:.6f}")
    logger.info(f"Target Rank in Vocab: {sample_res_cms['target_rank']} / {model_cms.vocab_size}")
    logger.info(f"Top 5 Predicted Tokens: {sample_res_cms['top5_tokens']}")
    logger.info(f"Top 5 Probabilities: {sample_res_cms['top5_probs']}")
    logger.info(f"Evaluator Exact Match: {sample_res_cms['is_correct']}")

    # Comparison
    logger.info("\n" + "=" * 80)
    logger.info("SINGLE SAMPLE VALIDATION COMPARISON SUMMARY")
    logger.info("=" * 80)
    logger.info(f"{'Metric':<30} | {'Level 1 (ICL Baseline)':<22} | {'Level 2 (CMS Adaptation)':<22}")
    logger.info("-" * 80)
    logger.info(f"{'Target Probability':<30} | {sample_res_icl['target_prob']:<22.6f} | {sample_res_cms['target_prob']:<22.6f}")
    logger.info(f"{'Target Rank in 49k Vocab':<30} | {sample_res_icl['target_rank']:<22d} | {sample_res_cms['target_rank']:<22d}")
    logger.info(f"{'Generated Answer':<30} | '{sample_res_icl['generated_answer']}':<20 | '{sample_res_cms['generated_answer']}':<20")
    logger.info(f"{'Evaluator Correct':<30} | {str(sample_res_icl['is_correct']):<22} | {str(sample_res_cms['is_correct']):<22}")
    logger.info(f"{'VRAM Allocated (MB)':<30} | {vram_icl:<22.2f} | {vram_cms:<22.2f}")
    logger.info("=" * 80)

    log_path = os.path.join(log_dir, filename)
    logger.info(f"Validation completed successfully. Log: {log_path}")


if __name__ == "__main__":
    debug_pretrained_sample()
