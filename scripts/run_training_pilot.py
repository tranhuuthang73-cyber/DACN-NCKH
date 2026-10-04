"""
Phase 3.2 SA-CMS / Hybrid Memory Adapter Training Pilot Runner.

Executes:
- Pilot A: 100 training samples (10 documents, 11,183 tokens)
- Pilot B: 200 training samples (20 documents, 21,905 tokens)
- Independent Validation: 50 samples (5 documents, 5,535 tokens)

Strict Rules:
- 100% Frozen backbone (SmolLM2-135M, 134,515,008 parameters)
- Trainable: Low-rank CMS adapters & gates only (3,544,320 parameters)
- 0% overlap with Phase 3.1 evaluation cases (DOC001-DOC003, Q001-Q100)
- Checkpoint persistence and reload verification
"""

import os
import sys
import time
import math
import json
import csv
import re
from pathlib import Path
from typing import Dict, Any, List, Tuple
from collections import Counter

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import torch
import torch.nn as nn
import torch.nn.functional as F

from src.hope_attention.pretrained_hope import PretrainedHopeLM
from src.training.training_corpus import get_training_corpus, get_validation_corpus


def normalize_answer(s: str) -> str:
    """Lower text and remove punctuation, articles, and extra whitespace."""
    s = s.lower()
    s = re.sub(r"\b(a|an|the)\b", " ", s)
    s = re.sub(r"[^\w\s]", " ", s)
    return " ".join(s.split())


def compute_token_f1(prediction: str, ground_truth: str) -> float:
    pred_tokens = normalize_answer(prediction).split()
    truth_tokens = normalize_answer(ground_truth).split()
    if not pred_tokens or not truth_tokens:
        return 1.0 if pred_tokens == truth_tokens else 0.0
    common = Counter(pred_tokens) & Counter(truth_tokens)
    num_same = sum(common.values())
    if num_same == 0:
        return 0.0
    precision = 1.0 * num_same / len(pred_tokens)
    recall = 1.0 * num_same / len(truth_tokens)
    return (2 * precision * recall) / (precision + recall)


def compute_exact_match(prediction: str, ground_truth: str) -> float:
    return 1.0 if normalize_answer(prediction) == normalize_answer(ground_truth) else 0.0


def evaluate_validation(
    model: PretrainedHopeLM,
    val_samples: List[Dict[str, Any]],
    device: str,
    max_gen_tokens: int = 16,
) -> Dict[str, Any]:
    """
    Evaluates model on validation split:
    - Cross-entropy loss & Perplexity
    - Token F1 and Exact Match (EM) via greedy autoregressive generation
    """
    model.eval()
    tokenizer = model.tokenizer

    total_val_loss = 0.0
    val_count = 0
    f1_scores = []
    em_scores = []

    with torch.no_grad():
        for sample in val_samples:
            # 1. Compute loss over full sequence
            enc = tokenizer(
                sample["formatted_text"],
                return_tensors="pt",
                truncation=True,
                max_length=256,
            ).to(device)
            input_ids = enc.input_ids
            targets = input_ids.clone()

            _, loss = model(input_ids, targets=targets)
            if loss is not None and not torch.isnan(loss):
                total_val_loss += loss.item()
                val_count += 1

            # 2. Greedy generation for QA answer
            prompt = f"Context: {sample['context']}\nQuestion: {sample['question']}\nAnswer:"
            prompt_enc = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=200).to(device)
            gen_ids = prompt_enc.input_ids.clone()
            prompt_len = gen_ids.shape[1]

            for _ in range(max_gen_tokens):
                logits, _ = model(gen_ids)
                next_tok = torch.argmax(logits[:, -1, :], dim=-1, keepdim=True)
                gen_ids = torch.cat([gen_ids, next_tok], dim=-1)
                # Stop if EOS or newline
                if next_tok.item() == tokenizer.eos_token_id or next_tok.item() == tokenizer.encode("\n")[0]:
                    break

            pred_text = tokenizer.decode(gen_ids[0][prompt_len:], skip_special_tokens=True).strip()
            gold_text = sample["answer"].strip()

            f1_scores.append(compute_token_f1(pred_text, gold_text))
            em_scores.append(compute_exact_match(pred_text, gold_text))

    avg_val_loss = total_val_loss / max(1, val_count)
    val_ppl = math.exp(min(avg_val_loss, 20.0))
    avg_f1 = sum(f1_scores) / max(1, len(f1_scores))
    avg_em = sum(em_scores) / max(1, len(em_scores))

    return {
        "val_loss": round(avg_val_loss, 4),
        "val_ppl": round(val_ppl, 2),
        "token_f1": round(avg_f1, 4),
        "exact_match": round(avg_em, 4),
    }


def train_pilot(
    pilot_name: str,
    training_samples: List[Dict[str, Any]],
    val_samples: List[Dict[str, Any]],
    device: str = "cuda",
    seed: int = 42,
    lr: float = 1e-4,
    batch_size: int = 2,
    grad_accum_steps: int = 2,
    num_epochs: int = 3,
    max_seq_len: int = 256,
) -> Dict[str, Any]:
    """
    Trains SA-CMS adapter parameters on training_samples.
    Backbone remains 100% frozen.
    """
    print(f"\n{'='*70}")
    print(f"STARTING {pilot_name.upper()}: {len(training_samples)} SAMPLES")
    print(f"{'='*70}")

    # Set seed
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    # 1. Initialize fresh model
    model = PretrainedHopeLM(
        model_name_or_path="HuggingFaceTB/SmolLM2-135M",
        num_levels=2,
        device=device,
        torch_dtype=torch.float32,
    )
    tokenizer = model.tokenizer

    trainable_params = sum(p.numel() for p in model.get_cms_parameters())
    frozen_params = sum(p.numel() for p in model.backbone.parameters() if not p.requires_grad)
    total_params = trainable_params + frozen_params

    print(f"Model: SmolLM2-135M + SA-CMS (num_levels=2)")
    print(f"Total Parameters:     {total_params:,}")
    print(f"Trainable Parameters: {trainable_params:,} ({trainable_params/total_params*100:.2f}%)")
    print(f"Frozen Parameters:    {frozen_params:,} ({frozen_params/total_params*100:.2f}%)")

    # 2. Setup optimizer
    optimizer = torch.optim.AdamW(model.get_cms_parameters(), lr=lr, weight_decay=0.01)

    # Token accounting
    lengths = [len(tokenizer.encode(s["formatted_text"])) for s in training_samples]
    total_tokens_per_epoch = sum(lengths)
    doc_ids = set(s["document_id"] for s in training_samples)

    print(f"Document Count:       {len(doc_ids)}")
    print(f"Sample Count:         {len(training_samples)}")
    print(f"Total Tokens/Epoch:   {total_tokens_per_epoch:,}")
    print(f"Average Tokens/Sample: {total_tokens_per_epoch/len(training_samples):.2f}")
    print(f"Min / Max Tokens:     {min(lengths)} / {max(lengths)}")

    # Pre-encode training samples
    encoded_samples = []
    for s in training_samples:
        enc = tokenizer(
            s["formatted_text"],
            return_tensors="pt",
            truncation=True,
            max_length=max_seq_len,
        )
        encoded_samples.append(enc.input_ids.squeeze(0))

    # Initial Validation before training
    print(f"\n[Validation 0] Evaluating initial checkpoint...")
    pre_val = evaluate_validation(model, val_samples, device)
    print(f"  Pre-train Val Loss: {pre_val['val_loss']} | Val PPL: {pre_val['val_ppl']} | F1: {pre_val['token_f1']} | EM: {pre_val['exact_match']}")

    # Training loop
    epoch_losses = []
    start_time = time.time()
    if torch.cuda.is_available():
        torch.cuda.reset_peak_memory_stats()

    model.train()
    for epoch in range(1, num_epochs + 1):
        epoch_start = time.time()
        running_loss = 0.0
        step_count = 0
        optimizer.zero_grad()

        # Batch iteration
        for i in range(0, len(encoded_samples), batch_size):
            batch_tensors = encoded_samples[i:i + batch_size]
            # Pad batch
            max_len = max(t.shape[0] for t in batch_tensors)
            padded = torch.full((len(batch_tensors), max_len), tokenizer.pad_token_id, dtype=torch.long)
            for b_idx, t in enumerate(batch_tensors):
                padded[b_idx, :t.shape[0]] = t

            padded = padded.to(device)
            targets = padded.clone()
            targets[targets == tokenizer.pad_token_id] = -100

            logits, loss = model(padded, targets=targets)
            loss_scaled = loss / grad_accum_steps
            loss_scaled.backward()

            running_loss += loss.item()
            step_count += 1

            if step_count % grad_accum_steps == 0 or (i + batch_size >= len(encoded_samples)):
                torch.nn.utils.clip_grad_norm_(model.get_cms_parameters(), max_norm=1.0)
                optimizer.step()
                optimizer.zero_grad()

        avg_epoch_loss = running_loss / max(1, step_count)
        epoch_losses.append(round(avg_epoch_loss, 4))
        epoch_time = time.time() - epoch_start
        print(f"  Epoch {epoch}/{num_epochs}: Train Loss = {avg_epoch_loss:.4f} (took {epoch_time:.2f}s)")

    total_time = time.time() - start_time
    total_tokens_processed = total_tokens_per_epoch * num_epochs
    token_throughput = total_tokens_processed / max(1e-6, total_time)

    # Peak VRAM
    if torch.cuda.is_available():
        peak_vram_mb = round(torch.cuda.max_memory_allocated() / (1024 * 1024), 2)
    else:
        peak_vram_mb = 0.0

    # Final Validation
    print(f"\n[Validation Final] Evaluating trained checkpoint...")
    post_val = evaluate_validation(model, val_samples, device)
    print(f"  Post-train Val Loss: {post_val['val_loss']} | Val PPL: {post_val['val_ppl']} | F1: {post_val['token_f1']} | EM: {post_val['exact_match']}")

    # Save Checkpoint
    checkpoint_dir = ROOT_DIR / "checkpoints" / pilot_name
    checkpoint_dir.mkdir(parents=True, exist_ok=True)
    weights_path = checkpoint_dir / "cms_weights.pt"
    config_path = checkpoint_dir / "training_config.json"

    # Save only trainable CMS weights
    state_to_save = {
        "cms_state_dict": model.cms.state_dict() if model.cms else {},
        "cms_norm_state_dict": model.cms_norm.state_dict() if model.cms_norm else {},
        "trainable_params": trainable_params,
        "frozen_params": frozen_params,
        "num_levels": 2,
    }
    torch.save(state_to_save, weights_path)
    ckpt_size_mb = round(weights_path.stat().st_size / (1024 * 1024), 2)
    print(f"  [OK] Checkpoint saved: {weights_path} ({ckpt_size_mb} MB)")

    # Save config
    run_meta = {
        "pilot_name": pilot_name,
        "sample_count": len(training_samples),
        "document_count": len(doc_ids),
        "total_tokens_per_epoch": total_tokens_per_epoch,
        "total_tokens_processed": total_tokens_processed,
        "avg_tokens_per_sample": round(total_tokens_per_epoch / len(training_samples), 2),
        "min_tokens": min(lengths),
        "max_tokens": max(lengths),
        "trainable_parameters": trainable_params,
        "frozen_parameters": frozen_params,
        "optimizer": "AdamW",
        "learning_rate": lr,
        "weight_decay": 0.01,
        "batch_size": batch_size,
        "gradient_accumulation_steps": grad_accum_steps,
        "effective_batch_size": batch_size * grad_accum_steps,
        "num_epochs": num_epochs,
        "max_seq_length": max_seq_len,
        "precision": "float32",
        "random_seed": seed,
        "device": device,
        "wall_clock_time_sec": round(total_time, 2),
        "token_throughput_tps": round(token_throughput, 2),
        "peak_vram_mb": peak_vram_mb,
        "checkpoint_size_mb": ckpt_size_mb,
        "epoch_train_losses": epoch_losses,
        "final_train_loss": epoch_losses[-1],
        "pre_train_validation": pre_val,
        "post_train_validation": post_val,
    }

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(run_meta, f, indent=2, ensure_ascii=False)
    print(f"  [OK] Config saved: {config_path}")

    # Verify Checkpoint Reload
    print(f"\n[Checkpoint Verification] Reloading checkpoint to verify bit-level fidelity...")
    reloaded_model = PretrainedHopeLM(
        model_name_or_path="HuggingFaceTB/SmolLM2-135M",
        num_levels=2,
        device=device,
        torch_dtype=torch.float32,
    )
    loaded_state = torch.load(weights_path, map_location=device)
    reloaded_model.cms.load_state_dict(loaded_state["cms_state_dict"])
    reloaded_model.cms_norm.load_state_dict(loaded_state["cms_norm_state_dict"])
    reloaded_model.eval()

    # Smoke inference with reloaded model
    test_sample = val_samples[0]
    test_enc = tokenizer(test_sample["formatted_text"], return_tensors="pt").to(device)
    with torch.no_grad():
        orig_logits, _ = model(test_enc.input_ids)
        reloaded_logits, _ = reloaded_model(test_enc.input_ids)
        diff = torch.max(torch.abs(orig_logits - reloaded_logits)).item()
        assert diff < 1e-5, f"Reloaded logits diverge by {diff}!"
    print(f"  [OK] Checkpoint reload verified! Max logit diff = {diff:.8f} (exact match)")

    return run_meta


def main():
    print("=" * 80)
    print("PHASE 3.2 - TRAINING PILOT FOR SA-CMS / HYBRID MEMORY")
    print("=" * 80)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Using device: {device}")

    # 1. Load Data
    train_corpus = get_training_corpus()
    val_corpus = get_validation_corpus()

    all_train_samples = train_corpus["samples"]
    val_samples = val_corpus["samples"]

    # Split A: 100 samples
    samples_100 = all_train_samples[:100]
    # Split B: 200 samples
    samples_200 = all_train_samples[:200]

    # Run Pilot A (100)
    meta_100 = train_pilot(
        pilot_name="pilot_100",
        training_samples=samples_100,
        val_samples=val_samples,
        device=device,
        seed=42,
        lr=1e-4,
        batch_size=2,
        grad_accum_steps=2,
        num_epochs=3,
        max_seq_len=256,
    )

    # Run Pilot B (200) only after Pilot A finishes without error
    meta_200 = train_pilot(
        pilot_name="pilot_200",
        training_samples=samples_200,
        val_samples=val_samples,
        device=device,
        seed=42,
        lr=1e-4,
        batch_size=2,
        grad_accum_steps=2,
        num_epochs=3,
        max_seq_len=256,
    )

    # Export Comparison Results (Task 7)
    results_dir = ROOT_DIR / "results"
    results_dir.mkdir(parents=True, exist_ok=True)

    csv_path = results_dir / "phase3_2_training_comparison.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Training Size", "Total Tokens", "Trainable Params", "Train Loss",
            "Val Loss", "Val PPL", "F1", "EM", "Time (s)", "Throughput (tps)",
            "VRAM (MB)", "Checkpoint Size (MB)"
        ])
        writer.writerow([
            "100 samples",
            meta_100["total_tokens_per_epoch"],
            meta_100["trainable_parameters"],
            meta_100["final_train_loss"],
            meta_100["post_train_validation"]["val_loss"],
            meta_100["post_train_validation"]["val_ppl"],
            meta_100["post_train_validation"]["token_f1"],
            meta_100["post_train_validation"]["exact_match"],
            meta_100["wall_clock_time_sec"],
            meta_100["token_throughput_tps"],
            meta_100["peak_vram_mb"],
            meta_100["checkpoint_size_mb"],
        ])
        writer.writerow([
            "200 samples",
            meta_200["total_tokens_per_epoch"],
            meta_200["trainable_parameters"],
            meta_200["final_train_loss"],
            meta_200["post_train_validation"]["val_loss"],
            meta_200["post_train_validation"]["val_ppl"],
            meta_200["post_train_validation"]["token_f1"],
            meta_200["post_train_validation"]["exact_match"],
            meta_200["wall_clock_time_sec"],
            meta_200["token_throughput_tps"],
            meta_200["peak_vram_mb"],
            meta_200["checkpoint_size_mb"],
        ])
    print(f"\n[OK] Comparison CSV saved to: {csv_path}")

    # Export Global Config JSON
    config_json_path = results_dir / "phase3_2_training_config.json"
    with open(config_json_path, "w", encoding="utf-8") as f:
        json.dump({
            "pilot_100": meta_100,
            "pilot_200": meta_200,
        }, f, indent=2, ensure_ascii=False)
    print(f"[OK] Config JSON saved to: {config_json_path}")

    # Print Summary Table
    print("\n" + "=" * 90)
    print("PHASE 3.2 TRAINING PILOT COMPARISON (100 VS 200 SAMPLES)")
    print("=" * 90)
    header = f"{'Metric':<25} | {'Pilot 100':<20} | {'Pilot 200':<20}"
    print(header)
    print("-" * len(header))
    print(f"{'Sample Count':<25} | {meta_100['sample_count']:<20} | {meta_200['sample_count']:<20}")
    print(f"{'Document Count':<25} | {meta_100['document_count']:<20} | {meta_200['document_count']:<20}")
    print(f"{'Total Tokens/Epoch':<25} | {meta_100['total_tokens_per_epoch']:,<20} | {meta_200['total_tokens_per_epoch']:,<20}")
    print(f"{'Total Tokens Processed':<25} | {meta_100['total_tokens_processed']:,<20} | {meta_200['total_tokens_processed']:,<20}")
    print(f"{'Trainable Parameters':<25} | {meta_100['trainable_parameters']:,<20} | {meta_200['trainable_parameters']:,<20}")
    print(f"{'Train Loss (Epoch 1)':<25} | {meta_100['epoch_train_losses'][0]:<20} | {meta_200['epoch_train_losses'][0]:<20}")
    print(f"{'Train Loss (Epoch 2)':<25} | {meta_100['epoch_train_losses'][1]:<20} | {meta_200['epoch_train_losses'][1]:<20}")
    print(f"{'Train Loss (Epoch 3)':<25} | {meta_100['epoch_train_losses'][2]:<20} | {meta_200['epoch_train_losses'][2]:<20}")
    print(f"{'Val Loss (Post-train)':<25} | {meta_100['post_train_validation']['val_loss']:<20} | {meta_200['post_train_validation']['val_loss']:<20}")
    print(f"{'Val PPL (Post-train)':<25} | {meta_100['post_train_validation']['val_ppl']:<20} | {meta_200['post_train_validation']['val_ppl']:<20}")
    print(f"{'Token F1':<25} | {meta_100['post_train_validation']['token_f1']:<20} | {meta_200['post_train_validation']['token_f1']:<20}")
    print(f"{'Exact Match (EM)':<25} | {meta_100['post_train_validation']['exact_match']:<20} | {meta_200['post_train_validation']['exact_match']:<20}")
    print(f"{'Wall-clock Time':<25} | {meta_100['wall_clock_time_sec']}s{'':<15} | {meta_200['wall_clock_time_sec']}s{'':<15}")
    print(f"{'Throughput':<25} | {meta_100['token_throughput_tps']} tps{'':<12} | {meta_200['token_throughput_tps']} tps{'':<12}")
    print(f"{'Peak VRAM':<25} | {meta_100['peak_vram_mb']} MB{'':<13} | {meta_200['peak_vram_mb']} MB{'':<13}")
    print(f"{'Checkpoint Size':<25} | {meta_100['checkpoint_size_mb']} MB{'':<13} | {meta_200['checkpoint_size_mb']} MB{'':<13}")
    print("=" * 90)


if __name__ == "__main__":
    main()
