"""
Diagnostic script for MK-NIAH pipeline auditing and root cause analysis.
Validates:
1. Dataset generation, needle placement, and context construction
2. Prompt and token formatting
3. Context truncation check
4. Model forward and logits distribution
5. Evaluator and answer extraction
6. Memory update verification (checking whether CMS weights actually changed)
7. Checkpoint loading verification
8. Ingestion & CMS memorization test
"""

import os
import sys

# Ensure workspace root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import torch
import yaml
from typing import Dict, Any

from src.hope_attention.model import HopeAttentionLM
from src.evaluation.mk_niah import MKNIAHBenchmark
from src.training.online_trainer import OnlineDocumentTrainer
from src.utils.logger import setup_logger
from src.utils.checkpoint import load_checkpoint


def run_mkniah_diagnostics() -> Dict[str, Any]:
    logger = setup_logger(name="debug_mkniah", log_dir="logs")
    logger.info("==================================================")
    logger.info("=== STARTING MK-NIAH AUDIT & ROOT CAUSE DEBUG ===")
    logger.info("==================================================")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logger.info(f"Execution Device: {device}")

    # Load baseline config
    with open("configs/baseline_config.yaml", "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    vocab_size = cfg["model"]["vocab_size"]
    max_seq_len = cfg["model"]["max_seq_len"]

    # ----------------------------------------------------
    # AUDIT ITEM 1 & 2: Sample Generation & Manual Trace
    # ----------------------------------------------------
    logger.info("\n--- [AUDIT ITEM 1 & 2] MANUAL SAMPLE TRACE ---")
    bench = MKNIAHBenchmark(
        vocab_size=vocab_size,
        needle_key_start=100,
        needle_val_start=500,
        haystack_token_start=10,
        haystack_token_end=90,
        seed=42,
    )

    context_len = 128
    num_needles = 3
    input_ids, target_vals, query_keys = bench.generate_sample(
        context_length=context_len,
        num_needles=num_needles,
    )
    tokens = input_ids[0].tolist()
    seq_len = len(tokens)

    logger.info(f"Generated Sequence Length: {seq_len} tokens (Context budget: {context_len})")
    logger.info(f"Model Max Sequence Length: {max_seq_len} tokens")

    # Check Truncation
    is_truncated = seq_len > max_seq_len
    logger.info(f"Is Context Truncated?: {is_truncated} (seq_len {seq_len} <= {max_seq_len})")

    # Find needle locations in haystack
    logger.info(f"Queried Key: {query_keys[0]}")
    logger.info(f"Expected Target Value: {target_vals[0]}")

    logger.info("\nInspecting Needle Placements in Sequence:")
    for k_idx, k in enumerate(query_keys):
        k_positions = [i for i, tok in enumerate(tokens) if tok == k]
        v_positions = [i for i, tok in enumerate(tokens) if tok == target_vals[k_idx]]
        logger.info(f"  Needle [{k} -> {target_vals[k_idx]}]: Key at index {k_positions}, Value at index {v_positions}")
        if v_positions:
            ctx_start = max(0, v_positions[0] - 3)
            ctx_end = min(seq_len, v_positions[0] + 4)
            logger.info(f"  Local Context around needle: {tokens[ctx_start:ctx_end]}")

    logger.info(f"Prompt Tail (last 8 tokens): {tokens[-8:]}")
    logger.info(f"Final Query Token (at index {seq_len - 1}): {tokens[-1]}")

    # ----------------------------------------------------
    # AUDIT ITEM 3: Model Forward & Output Distribution
    # ----------------------------------------------------
    logger.info("\n--- [AUDIT ITEM 3] MODEL FORWARD & LOGITS DISTRIBUTION ---")
    model = HopeAttentionLM(
        vocab_size=vocab_size,
        d_model=cfg["model"]["d_model"],
        n_heads=cfg["model"]["n_heads"],
        n_layers=cfg["model"]["n_layers"],
        d_ff=cfg["model"]["d_ff"],
        num_levels=cfg["cms"]["num_levels"],
        lowest_chunk_size=cfg["cms"]["lowest_chunk_size"],
        base_lr=cfg["cms"]["base_lr"],
        max_seq_len=max_seq_len,
    ).to(device)
    model.eval()

    input_tensor = input_ids.to(device)
    with torch.no_grad():
        logits, _, _ = model(input_tensor)

    last_logits = logits[0, -1, :]  # Shape: (vocab_size,)
    probs = torch.softmax(last_logits, dim=-1)

    top5_probs, top5_tokens = torch.topk(probs, 5)
    pred_token = top5_tokens[0].item()
    pred_prob = top5_probs[0].item()

    target_token = target_vals[0]
    target_prob = probs[target_token].item()

    # Calculate rank of target token among all vocab tokens
    sorted_indices = torch.argsort(last_logits, descending=True)
    target_rank = (sorted_indices == target_token).nonzero(as_tuple=True)[0].item() + 1

    logger.info(f"Target Token: {target_token} | Predicted Token (Argmax): {pred_token}")
    logger.info(f"Target Token Probability: {target_prob:.6f} (Random chance = {1.0/vocab_size:.6f})")
    logger.info(f"Target Token Rank in Vocabulary: {target_rank} / {vocab_size}")
    logger.info(f"Top 5 Predicted Tokens: {top5_tokens.tolist()} with Probs: {[round(p, 5) for p in top5_probs.tolist()]}")
    logger.info(f"Evaluator Exact Match Result: {pred_token == target_token}")

    # ----------------------------------------------------
    # AUDIT ITEM 4: Memory Update Verification
    # ----------------------------------------------------
    logger.info("\n--- [AUDIT ITEM 4] MEMORY UPDATE AUDIT (Equation 71) ---")
    # Record CMS weights before calling bench.evaluate_model
    fastest_level = cfg["cms"]["num_levels"] - 1
    w_before = model.blocks[0].cms.chain.blocks[fastest_level].w1.weight.detach().clone()

    eval_result = bench.evaluate_model(
        model=model,
        num_samples=1,
        context_length=context_len,
        num_needles=num_needles,
        device=device,
    )
    w_after = model.blocks[0].cms.chain.blocks[fastest_level].w1.weight.detach().clone()
    param_diff = torch.norm(w_after - w_before).item()

    logger.info(f"Parameter Norm Difference in CMS during evaluate_model(): {param_diff:.10f}")
    if param_diff == 0.0:
        logger.error(">>> CRITICAL FINDING: CMS parameters were NOT updated during evaluate_model()! <<<")
        logger.error(">>> In bench.evaluate_model(), torch.no_grad() was used and update_cms_online was never called! <<<")
    else:
        logger.info("CMS parameters were updated during evaluation.")

    # ----------------------------------------------------
    # AUDIT ITEM 5: Checkpoint Loading Check
    # ----------------------------------------------------
    logger.info("\n--- [AUDIT ITEM 5] CHECKPOINT INTEGRITY CHECK ---")
    ckpt_path = "checkpoints/level_3_cms.pt"
    if os.path.exists(ckpt_path):
        fresh_model = HopeAttentionLM(
            vocab_size=vocab_size,
            d_model=cfg["model"]["d_model"],
            n_heads=cfg["model"]["n_heads"],
            n_layers=cfg["model"]["n_layers"],
            d_ff=cfg["model"]["d_ff"],
            num_levels=3,
            lowest_chunk_size=64,
            max_seq_len=max_seq_len,
        ).to(device)
        loaded = load_checkpoint(ckpt_path, fresh_model, device=device)
        logger.info(f"Checkpoint loaded successfully from {ckpt_path}.")
        logger.info(f"Checkpoint config metadata: {loaded.get('config', {})}")
        logger.info(f"Checkpoint saved metrics: {loaded.get('metrics', {})}")
    else:
        logger.warn(f"Checkpoint {ckpt_path} does not exist on disk.")

    # ----------------------------------------------------
    # AUDIT ITEM 6: Can CMS Actually Memorize the Needle?
    # ----------------------------------------------------
    logger.info("\n--- [AUDIT ITEM 6] CMS MEMORIZATION CAPACITY TEST ---")
    logger.info("Testing whether Equation 71 can memorize [query_key -> target_val] if updated properly:")

    test_model = HopeAttentionLM(
        vocab_size=vocab_size,
        d_model=cfg["model"]["d_model"],
        n_heads=cfg["model"]["n_heads"],
        n_layers=cfg["model"]["n_layers"],
        d_ff=cfg["model"]["d_ff"],
        num_levels=3,
        lowest_chunk_size=64,
        base_lr=0.05,
        max_seq_len=max_seq_len,
    ).to(device)

    needle_input = torch.tensor([[query_keys[0]]], device=device)
    needle_target = torch.tensor([[target_vals[0]]], device=device)

    # Initial state
    with torch.no_grad():
        init_logits, init_loss, _ = test_model(needle_input, targets=needle_target)
    init_prob = torch.softmax(init_logits[0, -1, :], dim=-1)[target_vals[0]].item()
    logger.info(f"  Step 0: Loss = {init_loss.item():.4f}, Target Prob = {init_prob:.6f}")

    # Take 10 online gradient steps on the needle pair
    for s in range(1, 11):
        _, step_loss, _ = test_model(needle_input, targets=needle_target)
        test_model.update_cms_online(step_loss, num_tokens=64)

    with torch.no_grad():
        final_logits, final_loss, _ = test_model(needle_input, targets=needle_target)
    final_prob = torch.softmax(final_logits[0, -1, :], dim=-1)[target_vals[0]].item()
    final_pred = torch.argmax(final_logits[0, -1, :]).item()

    logger.info(f"  Step 10: Loss = {final_loss.item():.4f}, Target Prob = {final_prob:.6f}")
    logger.info(f"  Target: {target_vals[0]} | Final Prediction: {final_pred} | Match: {final_pred == target_vals[0]}")

    # Test Reset
    test_model.reset_memory()
    with torch.no_grad():
        reset_logits, reset_loss, _ = test_model(needle_input, targets=needle_target)
    reset_pred = torch.argmax(reset_logits[0, -1, :]).item()
    logger.info(f"  After Reset: Prediction = {reset_pred} | Match Target: {reset_pred == target_vals[0]}")

    logger.info("\n=== DIAGNOSTICS COMPLETE ===")
    return {
        "seq_len": seq_len,
        "is_truncated": is_truncated,
        "param_diff_in_eval": param_diff,
        "target_prob_init": target_prob,
        "target_prob_after_update": final_prob,
        "final_pred_match": final_pred == target_vals[0],
    }


if __name__ == "__main__":
    run_mkniah_diagnostics()
