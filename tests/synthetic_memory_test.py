"""
Synthetic Memory & Retrieval Mechanism Validation for Hope-Attention / CMS.

DISCLAIMER:
This synthetic experiment is designed STRICTLY for technical mechanism validation
(Equation 70, 71, 74, information persistence, and memory reset).
It is NOT a paper reproduction result and must NOT be compared against paper figures.
"""

import os
import sys
from pathlib import Path
import datetime
import torch
import torch.nn.functional as F

# Ensure workspace root is in python path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.hope_attention.model import HopeAttentionLM
from src.utils.logger import setup_logger


def run_synthetic_memory_validation():
    # Setup logger
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = str(ROOT_DIR / "logs")
    filename = f"synthetic_memory_test_{timestamp}.log"
    logger = setup_logger("SyntheticMemoryTest", log_dir=log_dir, filename=filename)
    log_file = os.path.join(log_dir, filename)

    logger.info("=" * 80)
    logger.info("STARTING SYNTHETIC MEMORY & RETRIEVAL VALIDATION (TRACK 1)")
    logger.info("[DISCLAIMER] MECHANISM VALIDATION ONLY — NOT A PAPER REPRODUCTION RESULT")
    logger.info("=" * 80)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Using compute device: {device}")

    # Set deterministic seed
    torch.manual_seed(42)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(42)

    # 1. Initialize Micro HopeAttentionLM (Track 1)
    vocab_size = 1000
    d_model = 128
    n_layers = 4
    n_heads = 4
    num_levels = 3
    chunk_sizes = [64, 32, 16]
    frequencies = [1.0, 2.0, 4.0]

    model = HopeAttentionLM(
        vocab_size=vocab_size,
        d_model=d_model,
        n_layers=n_layers,
        n_heads=n_heads,
        d_ff=512,
        max_seq_len=512,
        num_levels=num_levels,
        chunk_sizes=chunk_sizes,
        base_lr=0.01,
    ).to(device)

    total_params = sum(p.numel() for p in model.parameters())
    cms_params = sum(p.numel() for p in model.get_cms_parameters())
    logger.info(f"Model initialized: Total Params = {total_params:,}, CMS Params = {cms_params:,}")

    # 2. Define synthetic needle pair and context
    # Needle association: Key token -> Value token
    needle_key = 116
    needle_val = 516

    # Create distractor context (haystack)
    distractors = torch.randint(10, 90, (60,), device=device)
    # Insert needle in context: [distractors_1, key, val, distractors_2]
    context_tokens = torch.cat([
        distractors[:30],
        torch.tensor([needle_key, needle_val], device=device),
        distractors[30:]
    ])

    # Query sequence: prompt ending with needle_key
    query_prompt = torch.cat([distractors[:15], torch.tensor([needle_key], device=device)]).unsqueeze(0)

    logger.info(f"Target Needle Pair: Key = {needle_key} -> Target Value = {needle_val}")
    logger.info(f"Context Length: {len(context_tokens)} tokens")
    logger.info(f"Query Prompt Length: {query_prompt.shape[1]} tokens (ending with key {needle_key})")

    # Helper function to evaluate query prediction
    def query_model(step_name: str):
        model.eval()
        with torch.no_grad():
            out = model(query_prompt)
            logits = out[0] if isinstance(out, (tuple, list)) else (out["logits"] if isinstance(out, dict) else out)
            last_logits = logits[0, -1, :]
            probs = F.softmax(last_logits, dim=-1)

            target_prob = probs[needle_val].item()
            target_logit = last_logits[needle_val].item()

            # Rank of target token (1-indexed)
            sorted_indices = torch.argsort(last_logits, descending=True)
            target_rank = (sorted_indices == needle_val).nonzero(as_tuple=True)[0].item() + 1

            # Top 5 predictions
            top5_probs, top5_indices = torch.topk(probs, k=5)
            top5_tokens = top5_indices.tolist()
            top5_prob_vals = [round(p, 5) for p in top5_probs.tolist()]

            argmax_pred = sorted_indices[0].item()
            is_match = (argmax_pred == needle_val)

            logger.info(f"[{step_name}] Target Prob: {target_prob:.6f} | Rank: {target_rank}/{vocab_size}")
            logger.info(f"[{step_name}] Top 5 Tokens: {top5_tokens} with Probs: {top5_prob_vals}")
            logger.info(f"[{step_name}] Argmax Pred: {argmax_pred} | Exact Match: {is_match}")

            return {
                "step": step_name,
                "target_prob": target_prob,
                "target_rank": target_rank,
                "argmax_pred": argmax_pred,
                "is_match": is_match,
                "top5_tokens": top5_tokens,
                "top5_probs": top5_prob_vals,
            }

    # -------------------------------------------------------------
    # TEST 1: Baseline Query (Before Ingestion / Random Initial State)
    # -------------------------------------------------------------
    logger.info("-" * 50)
    logger.info("TEST 1: Evaluating Query BEFORE Ingestion (Initial State)...")
    res_before = query_model("BEFORE_INGESTION")

    # Capture initial CMS weights snapshot
    initial_cms_weights = [p.clone().detach() for p in model.get_cms_parameters()]

    # -------------------------------------------------------------
    # TEST 2 & 3: CMS Online Ingestion & Memory Update (Equation 71)
    # -------------------------------------------------------------
    logger.info("-" * 50)
    logger.info("TEST 2: Executing CMS Memory Ingestion on Needle Pair (Equation 71)...")
    
    # Freeze backbone, optimize only CMS parameters
    for p in model.parameters():
        p.requires_grad = False
    for p in model.get_cms_parameters():
        p.requires_grad = True

    optimizer = torch.optim.SGD(model.get_cms_parameters(), lr=0.1, momentum=0.9)
    needle_seq = torch.tensor([[needle_key, needle_val]], device=device)

    model.train()
    loss_history = []
    for step in range(1, 16):
        optimizer.zero_grad()
        out = model(needle_seq)
        logits = out[0] if isinstance(out, (tuple, list)) else (out["logits"] if isinstance(out, dict) else out)
        loss = F.cross_entropy(logits[:, 0, :], needle_seq[:, 1])
        loss.backward()
        optimizer.step()
        loss_history.append(loss.item())
        if step in [1, 5, 10, 15]:
            logger.info(f"  Step {step:2d}/15: Cross-Entropy Loss = {loss.item():.4f}")

    # Verify parameter delta
    cms_delta = 0.0
    for p_init, p_curr in zip(initial_cms_weights, model.get_cms_parameters()):
        cms_delta += torch.norm(p_curr - p_init).item()
    logger.info(f"CMS Parameter Delta ||theta_after - theta_before||_2: {cms_delta:.6f}")
    assert cms_delta > 0, "ERROR: CMS parameters did not update!"

    # -------------------------------------------------------------
    # TEST 3: Query AFTER Ingestion (Information Persistence Verification)
    # -------------------------------------------------------------
    logger.info("-" * 50)
    logger.info("TEST 3: Evaluating Query AFTER Ingestion (Information Persistence)...")
    res_after = query_model("AFTER_INGESTION")

    # Assertions for Technical Validity
    assert res_after["target_prob"] > res_before["target_prob"], "Target prob did not increase!"
    assert res_after["target_rank"] < res_before["target_rank"], "Target rank did not improve!"
    assert res_after["is_match"] is True, f"Model failed to retrieve needle! Pred: {res_after['argmax_pred']}"
    logger.info("=> SUCCESS: Needle successfully retrieved into Top-1 prediction!")

    # -------------------------------------------------------------
    # TEST 4: Reset Memory (reset_memory() Verification)
    # -------------------------------------------------------------
    logger.info("-" * 50)
    logger.info("TEST 4: Calling model.reset_memory()...")
    model.reset_memory()

    reset_delta = 0.0
    for p_init, p_curr in zip(initial_cms_weights, model.get_cms_parameters()):
        reset_delta += torch.norm(p_curr - p_init).item()
    logger.info(f"Delta between reset parameters and original initial weights: {reset_delta:.10f}")
    assert reset_delta < 1e-6, f"ERROR: reset_memory did not restore initial weights! Delta: {reset_delta}"

    logger.info("Evaluating Query AFTER Memory Reset...")
    res_reset = query_model("AFTER_RESET")
    assert res_reset["is_match"] is False, "Memory was not cleared after reset!"
    logger.info("=> SUCCESS: Memory clean reset confirmed.")

    # -------------------------------------------------------------
    # SUMMARY TABLE
    # -------------------------------------------------------------
    logger.info("=" * 80)
    logger.info("SYNTHETIC MEMORY TEST RESULTS SUMMARY TABLE (TRACK 1)")
    logger.info("=" * 80)
    logger.info(f"{'Metric':<25} | {'Before Ingestion':<18} | {'After Ingestion':<18} | {'After Reset':<18}")
    logger.info("-" * 85)
    logger.info(f"{'Target Probability':<25} | {res_before['target_prob']:<18.6f} | {res_after['target_prob']:<18.6f} | {res_reset['target_prob']:<18.6f}")
    logger.info(f"{'Target Rank (in 1000)':<25} | {res_before['target_rank']:<18d} | {res_after['target_rank']:<18d} | {res_reset['target_rank']:<18d}")
    logger.info(f"{'Top-1 Prediction':<25} | {res_before['argmax_pred']:<18d} | {res_after['argmax_pred']:<18d} | {res_reset['argmax_pred']:<18d}")
    logger.info(f"{'Exact Match (516)':<25} | {str(res_before['is_match']):<18} | {str(res_after['is_match']):<18} | {str(res_reset['is_match']):<18}")
    logger.info(f"{'CMS Weights Delta':<25} | {'0.000000':<18} | {cms_delta:<18.6f} | {reset_delta:<18.10f}")
    logger.info("=" * 80)
    logger.info(f"All technical mechanism assertions PASSED.")
    logger.info(f"Log written to: {log_file}")

    return {
        "res_before": res_before,
        "res_after": res_after,
        "res_reset": res_reset,
        "cms_delta": cms_delta,
        "reset_delta": reset_delta,
        "log_file": str(log_file),
    }


if __name__ == "__main__":
    run_synthetic_memory_validation()
