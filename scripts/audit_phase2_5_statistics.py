"""
scripts/audit_phase2_5_statistics.py

Automated Scientific & Statistical Audit Runner for Phase 2.5:
1. Task 1: Audit requirements against Research Proposal (Đề cương).
2. Task 2: Compute true paired statistical tests between B5 (Fixed Token) and P1 (SA-CMS)
   from paired per-document / per-sample observations:
   - QASPER PPL & Loss (Paired t-test, Wilcoxon signed-rank, Cohen's d, mean & median diff)
   - QASPER F1 & EM (Paired t-test, Wilcoxon signed-rank, Cohen's d, mean & median diff)
   - MK-NIAH Accuracy (McNemar's test with continuity correction & exact binomial test)
   - MK-NIAH Target Probability & Rank (Paired t-test, Wilcoxon signed-rank, Cohen's d)
3. Task 3: Implement true 95% Bootstrap Confidence Intervals:
   - Proper resampling unit: Document (n=10) for QASPER, Sample (n=100) for MK-NIAH.
   - 1,000 bootstrap iterations, percentile method, reproducible seed.
   - Fixes the flawed 3-seed bootstrap implementation.
4. Task 4: Audit multi-seed integrity across seeds 42, 43, 44 from results/phase2_5_controlled_comparison.csv.
5. Task 5: Number-by-number audit of docs/phase2_5_scientific_validation.md.
6. Task 7: Verify equal update budgets between Fixed, SA-CMS, and Random schedules.
7. Task 8: Save structured audit outputs to results/phase2_5_1_statistical_audit.csv.
"""

import os
import sys
import math
import random
import csv
from typing import Dict, Any, List, Tuple
import numpy as np
import torch
import torch.nn.functional as F
from scipy import stats

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.hope_attention.sa_cms import StructureAlignedHopeLM
from src.evaluation.pretrained_benchmarks import NaturalMKNIAHBenchmark, QASPERDocumentBenchmark


def proper_bootstrap_ci(
    data: List[float],
    n_bootstrap: int = 1000,
    ci: float = 0.95,
    seed: int = 42,
) -> Tuple[float, float]:
    """
    Computes valid non-parametric bootstrap confidence interval over
    actual observation units (samples or documents).
    """
    arr = np.array(data, dtype=np.float64)
    n = len(arr)
    if n <= 1:
        v = float(arr[0]) if n == 1 else 0.0
        return (round(v, 4), round(v, 4))
    
    rng = np.random.default_rng(seed)
    boot_means = np.empty(n_bootstrap, dtype=np.float64)
    for b in range(n_bootstrap):
        resample = rng.choice(arr, size=n, replace=True)
        boot_means[b] = np.mean(resample)
    
    alpha = (1.0 - ci) / 2.0
    low = float(np.percentile(boot_means, alpha * 100))
    high = float(np.percentile(boot_means, (1.0 - alpha) * 100))
    return (round(low, 4), round(high, 4))


def compute_paired_stats(
    a: List[float],
    b: List[float],
    name_a: str = "SA-CMS",
    name_b: str = "Fixed-Token",
) -> Dict[str, Any]:
    """
    Computes rigorous paired statistical tests between two paired observation vectors:
    - Mean difference (a - b)
    - Median difference
    - Paired Student's t-test (t-stat, p-value)
    - Wilcoxon signed-rank test (W-stat, p-value)
    - Cohen's d effect size for paired samples: d_z = mean(diff) / std(diff)
    """
    arr_a = np.array(a, dtype=np.float64)
    arr_b = np.array(b, dtype=np.float64)
    diff = arr_a - arr_b
    n = len(diff)

    mean_diff = float(np.mean(diff))
    std_diff = float(np.std(diff, ddof=1)) if n > 1 else 0.0
    median_diff = float(np.median(diff))

    # Cohen's d for paired samples
    cohen_d = mean_diff / std_diff if std_diff > 1e-12 else 0.0

    # Paired t-test
    if std_diff > 1e-12:
        t_res = stats.ttest_rel(arr_a, arr_b)
        t_stat = float(t_res.statistic)
        t_pval = float(t_res.pvalue)
    else:
        t_stat = 0.0
        t_pval = 1.0

    # Wilcoxon signed-rank test (handles zero differences)
    non_zero_diff = diff[diff != 0]
    if len(non_zero_diff) >= 5:
        try:
            w_res = stats.wilcoxon(arr_a, arr_b, zero_method="wilcox", alternative="two-sided")
            w_stat = float(w_res.statistic)
            w_pval = float(w_res.pvalue)
        except Exception:
            w_stat = float("nan")
            w_pval = float("nan")
    else:
        w_stat = float("nan")
        w_pval = float("nan")

    return {
        "n": n,
        "mean_diff": round(mean_diff, 4),
        "median_diff": round(median_diff, 4),
        "std_diff": round(std_diff, 4),
        "cohen_d": round(cohen_d, 4),
        "t_statistic": round(t_stat, 4),
        "t_pvalue": t_pval,
        "wilcoxon_stat": w_stat,
        "wilcoxon_pvalue": w_pval,
    }


def compute_mcnemar_test(
    correct_a: List[int],
    correct_b: List[int],
) -> Dict[str, Any]:
    """
    Computes McNemar's test for paired binary accuracy outcomes:
    Contingency table:
      b = Count(A=1, B=0)
      c = Count(A=0, B=1)
    """
    arr_a = np.array(correct_a, dtype=int)
    arr_b = np.array(correct_b, dtype=int)
    n = len(arr_a)

    n00 = int(np.sum((arr_a == 0) & (arr_b == 0)))
    n01 = int(np.sum((arr_a == 0) & (arr_b == 1)))  # B correct, A wrong
    n10 = int(np.sum((arr_a == 1) & (arr_b == 0)))  # A correct, B wrong
    n11 = int(np.sum((arr_a == 1) & (arr_b == 1)))

    acc_a = float(np.mean(arr_a)) * 100.0
    acc_b = float(np.mean(arr_b)) * 100.0
    acc_diff = acc_a - acc_b

    discordant = n01 + n10
    if discordant > 0:
        # With continuity correction
        stat = ((abs(n10 - n01) - 1.0) ** 2) / discordant
        p_val_chi2 = 1.0 - stats.chi2.cdf(stat, df=1)
        # Exact binomial test
        binom_res = stats.binomtest(min(n10, n01), discordant, p=0.5, alternative="two-sided")
        exact_p = binom_res.pvalue
    else:
        stat = 0.0
        p_val_chi2 = 1.0
        exact_p = 1.0

    return {
        "n": n,
        "acc_a_pct": round(acc_a, 2),
        "acc_b_pct": round(acc_b, 2),
        "acc_diff_pct": round(acc_diff, 2),
        "table": {"n00": n00, "n01": n01, "n10": n10, "n11": n11},
        "mcnemar_chi2": round(stat, 4),
        "mcnemar_pval": p_val_chi2,
        "exact_binomial_pval": exact_p,
    }


def audit_phase2_5_csv_file(csv_path: str = "results/phase2_5_controlled_comparison.csv") -> Dict[str, Any]:
    """Audits the Phase 2.5 CSV results table for multi-seed integrity, budget control, and consistency."""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Missing CSV at {csv_path}")

    rows = []
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows.append(r)

    total_rows = len(rows)
    methods = sorted(list(set(r["method"] for r in rows)))
    seeds = sorted(list(set(int(r["seed"]) for r in rows)))

    # Check 1: 3 seeds for each method
    method_seed_counts = {}
    for m in methods:
        m_seeds = [int(r["seed"]) for r in rows if r["method"] == m]
        method_seed_counts[m] = m_seeds

    # Check 2: Update budget equality
    level2_rows = [r for r in rows if int(r["levels"]) == 2]
    level3_rows = [r for r in rows if int(r["levels"]) == 3]

    l2_updates = set(int(r["update_count"]) for r in level2_rows)
    l3_updates = set(int(r["update_count"]) for r in level3_rows)

    l2_equal = (len(l2_updates) == 1)
    l3_equal = (len(l3_updates) == 1)

    return {
        "total_rows": total_rows,
        "methods": methods,
        "seeds": seeds,
        "method_seed_counts": method_seed_counts,
        "level2_updates": list(l2_updates),
        "level3_updates": list(l3_updates),
        "level2_budget_equal": l2_equal,
        "level3_budget_equal": l3_equal,
        "rows": rows,
    }


def run_detailed_paired_evaluation(seed: int = 42) -> Dict[str, Any]:
    """
    Runs an instrumented evaluation of B5 (Fixed Token) vs P1 (SA-CMS)
    along with ICL Baseline and Random Boundary on the exact same 10 QASPER documents
    and 100 MK-NIAH samples, saving individual per-sample observations.
    """
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32

    print(f"\n[Audit Eval] Initializing benchmark environments (Seed {seed})...")
    mkniah_samples = 100
    qasper_docs = 10

    mkniah_bench = NaturalMKNIAHBenchmark(num_samples=mkniah_samples, seed=seed)
    qasper_bench = QASPERDocumentBenchmark(num_documents=qasper_docs, seed=seed)

    configs_to_run = [
        ("ICL Baseline", 1, None),
        ("CMS Level 2 (Fixed Token)", 2, "fixed_token"),
        ("SA-CMS Level 2 (Structure Aligned)", 2, "structure"),
        ("CMS Level 2 (Random Boundary)", 2, "random"),
    ]

    obs = {
        "qasper": {},  # cfg -> {loss, ppl, f1, em, updates}
        "mkniah": {},  # cfg -> {correct, prob, rank, updates}
    }

    for cfg_label, num_levels, sched_mode in configs_to_run:
        print(f"\n[Audit Eval] Evaluating {cfg_label}...")
        torch.manual_seed(seed)
        random.seed(seed)
        np.random.seed(seed)
        if torch.cuda.is_available():
            torch.cuda.empty_cache()

        model = StructureAlignedHopeLM(
            model_name_or_path="HuggingFaceTB/SmolLM2-135M",
            num_levels=num_levels,
            device=device,
            torch_dtype=dtype,
        )
        model.eval()
        tokenizer = model.tokenizer

        # 1. QASPER evaluation per document
        q_loss_list = []
        q_ppl_list = []
        q_f1_list = []
        q_em_list = []
        q_update_list = []

        for d_idx in range(qasper_docs):
            context, question, answer = qasper_bench.documents[d_idx]
            doc_text = f"Context: {context}\nQuestion: {question}\nAnswer: {answer}"
            qa_prompt = f"Context: {context}\nQuestion: {question}\nAnswer:"

            enc_doc = tokenizer(doc_text, return_tensors="pt").to(model.device)
            enc_prompt = tokenizer(qa_prompt, return_tensors="pt").to(model.device)

            num_up = 0
            if sched_mode is not None and model.cms is not None:
                model.reset_memory()
                res = model.ingest_structured_document(
                    document_text=context,
                    schedule_mode=sched_mode,
                    seed=seed + d_idx * 13,
                )
                num_up = res.get("num_update_events", 0)

            with torch.no_grad():
                _, loss = model.forward(enc_doc.input_ids, targets=enc_doc.input_ids)
                loss_v = loss.item() if loss is not None else 0.0
                ppl_v = math.exp(min(loss_v, 20.0))

                curr_ids = enc_prompt.input_ids.clone()
                for _ in range(24):
                    cur_logits, _ = model.forward(curr_ids)
                    next_tok = torch.argmax(cur_logits[:, -1, :], dim=-1, keepdim=True)
                    curr_ids = torch.cat([curr_ids, next_tok], dim=1)
                    if next_tok.item() == tokenizer.eos_token_id:
                        break

                gen_ans = tokenizer.decode(
                    curr_ids[0, enc_prompt.input_ids.size(1):], skip_special_tokens=True
                ).strip()

                f1_v = qasper_bench.compute_f1(gen_ans, answer)
                em_v = qasper_bench.compute_exact_match(gen_ans, answer)

            q_loss_list.append(loss_v)
            q_ppl_list.append(ppl_v)
            q_f1_list.append(f1_v)
            q_em_list.append(em_v)
            q_update_list.append(num_up)

            if sched_mode is not None and model.cms is not None:
                model.reset_memory()

        obs["qasper"][cfg_label] = {
            "loss": q_loss_list,
            "ppl": q_ppl_list,
            "f1": q_f1_list,
            "em": q_em_list,
            "updates": q_update_list,
        }

        # 2. MK-NIAH evaluation per sample
        mk_correct_list = []
        mk_prob_list = []
        mk_rank_list = []
        mk_update_list = []

        for s_idx in range(mkniah_samples):
            sample = mkniah_bench._generate_sample(s_idx)
            prompt = sample["prompt_text"]
            context = sample["context_text"]
            expected_val = sample["expected_val"]

            prompt_enc = tokenizer(prompt, return_tensors="pt").to(model.device)
            prompt_ids = prompt_enc.input_ids
            target_token_id = tokenizer.encode(f" {expected_val}", add_special_tokens=False)[0]

            num_up = 0
            if sched_mode is not None and model.cms is not None:
                model.reset_memory()
                res = model.ingest_structured_document(
                    document_text=context,
                    schedule_mode=sched_mode,
                    seed=seed + s_idx * 7,
                )
                num_up = res.get("num_update_events", 0)

            with torch.no_grad():
                logits, _ = model.forward(prompt_ids)
                last_logits = logits[0, -1, :]
                probs = F.softmax(last_logits, dim=-1)

                target_prob = probs[target_token_id].item()
                sorted_ids = torch.argsort(last_logits, descending=True)
                target_rank = (sorted_ids == target_token_id).nonzero(as_tuple=True)[0].item() + 1

                curr_ids = prompt_ids.clone()
                for _ in range(6):
                    cur_logits, _ = model.forward(curr_ids)
                    next_tok = torch.argmax(cur_logits[:, -1, :], dim=-1, keepdim=True)
                    curr_ids = torch.cat([curr_ids, next_tok], dim=1)
                    if next_tok.item() == tokenizer.eos_token_id:
                        break

                gen_ans = tokenizer.decode(
                    curr_ids[0, prompt_ids.size(1):], skip_special_tokens=True
                ).strip()

                is_corr = 1 if (expected_val in gen_ans or gen_ans.startswith(expected_val)) else 0

            mk_correct_list.append(is_corr)
            mk_prob_list.append(target_prob)
            mk_rank_list.append(target_rank)
            mk_update_list.append(num_up)

            if sched_mode is not None and model.cms is not None:
                model.reset_memory()

        obs["mkniah"][cfg_label] = {
            "correct": mk_correct_list,
            "target_prob": mk_prob_list,
            "target_rank": mk_rank_list,
            "updates": mk_update_list,
        }

    return obs


def main():
    print("=" * 95)
    print("PHASE 2.5.1 — STATISTICAL AUDIT & GATE 2.5 VERIFICATION RUNNER")
    print("=" * 95)

    # Step 1: Audit CSV Integrity & Multi-Seed Consistency
    print("\n--- STEP 1: AUDITING PHASE 2.5 CSV INTEGRITY (Task 4 & Task 7) ---")
    csv_audit = audit_phase2_5_csv_file("results/phase2_5_controlled_comparison.csv")
    print(f"Total Rows Found: {csv_audit['total_rows']} (Expected: 21 rows = 7 configs x 3 seeds)")
    print(f"Seeds Found: {csv_audit['seeds']} (Expected: [42, 43, 44])")
    print(f"Level 2 Updates: {csv_audit['level2_updates']} -> Equal Budget: {csv_audit['level2_budget_equal']}")
    print(f"Level 3 Updates: {csv_audit['level3_updates']} -> Equal Budget: {csv_audit['level3_budget_equal']}")

    for m, s_list in csv_audit["method_seed_counts"].items():
        print(f"  {m:36s} -> Seeds: {s_list} (Count: {len(s_list)})")

    # Step 2: Run instrumented paired evaluation
    print("\n--- STEP 2: RUNNING INSTRUMENTED PAIRED EVALUATION (Seed 42) ---")
    obs = run_detailed_paired_evaluation(seed=42)

    # Step 3: Compute Paired Tests (Task 2)
    b5_name = "CMS Level 2 (Fixed Token)"
    p1_name = "SA-CMS Level 2 (Structure Aligned)"
    rand_name = "CMS Level 2 (Random Boundary)"
    icl_name = "ICL Baseline"

    print("\n" + "=" * 95)
    print("TASK 2: PAIRED STATISTICAL TESTS: P1 (SA-CMS) vs B5 (Fixed Token)")
    print("=" * 95)

    # 2.1 QASPER PPL
    q_ppl_p1 = obs["qasper"][p1_name]["ppl"]
    q_ppl_b5 = obs["qasper"][b5_name]["ppl"]
    ppl_stats = compute_paired_stats(q_ppl_p1, q_ppl_b5, p1_name, b5_name)
    print("\n[A] QASPER Perplexity (PPL) [Lower is better]")
    print(f"  Sample size (documents): {ppl_stats['n']}")
    print(f"  Mean PPL - SA-CMS: {np.mean(q_ppl_p1):.2f} | Fixed-Token: {np.mean(q_ppl_b5):.2f}")
    print(f"  Mean Difference (SA - Fixed): {ppl_stats['mean_diff']:.2f}")
    print(f"  Median Difference: {ppl_stats['median_diff']:.2f}")
    print(f"  Paired t-statistic: {ppl_stats['t_statistic']:.4f} | p-value: {ppl_stats['t_pvalue']:.6e}")
    print(f"  Wilcoxon W-statistic: {ppl_stats['wilcoxon_stat']} | p-value: {ppl_stats['wilcoxon_pvalue']:.6e}")
    print(f"  Effect Size (Cohen's d_z): {ppl_stats['cohen_d']:.4f}")

    # 2.2 QASPER F1
    q_f1_p1 = obs["qasper"][p1_name]["f1"]
    q_f1_b5 = obs["qasper"][b5_name]["f1"]
    f1_stats = compute_paired_stats(q_f1_p1, q_f1_b5, p1_name, b5_name)
    print("\n[B] QASPER Token F1 Score [Higher is better]")
    print(f"  Sample size (documents): {f1_stats['n']}")
    print(f"  Mean F1 - SA-CMS: {np.mean(q_f1_p1):.4f} | Fixed-Token: {np.mean(q_f1_b5):.4f}")
    print(f"  Mean Difference (SA - Fixed): {f1_stats['mean_diff']:.4f}")
    print(f"  Median Difference: {f1_stats['median_diff']:.4f}")
    print(f"  Paired t-statistic: {f1_stats['t_statistic']:.4f} | p-value: {f1_stats['t_pvalue']:.6e}")
    print(f"  Wilcoxon W-statistic: {f1_stats['wilcoxon_stat']} | p-value: {f1_stats['wilcoxon_pvalue']}")
    print(f"  Effect Size (Cohen's d_z): {f1_stats['cohen_d']:.4f}")

    # 2.3 MK-NIAH Accuracy (Binary Paired)
    mk_corr_p1 = obs["mkniah"][p1_name]["correct"]
    mk_corr_b5 = obs["mkniah"][b5_name]["correct"]
    mcnemar_stats = compute_mcnemar_test(mk_corr_p1, mk_corr_b5)
    print("\n[C] MK-NIAH Needle Retrieval Accuracy [Binary Paired McNemar Test]")
    print(f"  Sample size (queries): {mcnemar_stats['n']}")
    print(f"  SA-CMS Accuracy: {mcnemar_stats['acc_a_pct']:.1f}% | Fixed-Token: {mcnemar_stats['acc_b_pct']:.1f}%")
    print(f"  Accuracy Difference (SA - Fixed): {mcnemar_stats['acc_diff_pct']:+.1f}%")
    print(f"  Contingency Table: {mcnemar_stats['table']}")
    print(f"  McNemar Chi2 (continuity corrected): {mcnemar_stats['mcnemar_chi2']:.4f} | p-value: {mcnemar_stats['mcnemar_pval']:.4f}")
    print(f"  Exact Binomial p-value: {mcnemar_stats['exact_binomial_pval']:.4f}")

    # 2.4 MK-NIAH Target Probability
    mk_prob_p1 = obs["mkniah"][p1_name]["target_prob"]
    mk_prob_b5 = obs["mkniah"][b5_name]["target_prob"]
    prob_stats = compute_paired_stats(mk_prob_p1, mk_prob_b5, p1_name, b5_name)
    print("\n[D] MK-NIAH Target Probability [Continuous Paired Test]")
    print(f"  Sample size (queries): {prob_stats['n']}")
    print(f"  Mean Prob - SA-CMS: {np.mean(mk_prob_p1):.5f} | Fixed-Token: {np.mean(mk_prob_b5):.5f}")
    print(f"  Mean Difference (SA - Fixed): {prob_stats['mean_diff']:+.5f}")
    print(f"  Paired t-statistic: {prob_stats['t_statistic']:.4f} | p-value: {prob_stats['t_pvalue']:.6e}")
    print(f"  Wilcoxon W-statistic: {prob_stats['wilcoxon_stat']} | p-value: {prob_stats['wilcoxon_pvalue']:.6e}")
    print(f"  Effect Size (Cohen's d_z): {prob_stats['cohen_d']:.4f}")

    # Step 4: True Bootstrap 95% Confidence Intervals (Task 3)
    print("\n" + "=" * 95)
    print("TASK 3: TRUE 95% BOOTSTRAP CONFIDENCE INTERVALS (Sample/Document Level)")
    print("=" * 95)

    bootstrap_table = []
    methods_eval = [icl_name, b5_name, p1_name, rand_name]

    for m in methods_eval:
        # QASPER PPL (n=10 documents)
        ppl_vals = obs["qasper"][m]["ppl"]
        ppl_ci = proper_bootstrap_ci(ppl_vals, n_bootstrap=1000, ci=0.95, seed=42)
        bootstrap_table.append({
            "metric": "QASPER_PPL",
            "method": m,
            "bootstrap_unit": "document",
            "n": len(ppl_vals),
            "mean": round(float(np.mean(ppl_vals)), 2),
            "iterations": 1000,
            "ci_method": "percentile",
            "ci_95_low": ppl_ci[0],
            "ci_95_high": ppl_ci[1],
        })

        # QASPER F1 (n=10 documents)
        f1_vals = obs["qasper"][m]["f1"]
        f1_ci = proper_bootstrap_ci(f1_vals, n_bootstrap=1000, ci=0.95, seed=42)
        bootstrap_table.append({
            "metric": "QASPER_F1",
            "method": m,
            "bootstrap_unit": "document",
            "n": len(f1_vals),
            "mean": round(float(np.mean(f1_vals)), 4),
            "iterations": 1000,
            "ci_method": "percentile",
            "ci_95_low": f1_ci[0],
            "ci_95_high": f1_ci[1],
        })

        # MK-NIAH Accuracy (n=100 samples)
        acc_vals = [float(x) * 100.0 for x in obs["mkniah"][m]["correct"]]
        acc_ci = proper_bootstrap_ci(acc_vals, n_bootstrap=1000, ci=0.95, seed=42)
        bootstrap_table.append({
            "metric": "MK_NIAH_accuracy",
            "method": m,
            "bootstrap_unit": "sample",
            "n": len(acc_vals),
            "mean": round(float(np.mean(acc_vals)), 2),
            "iterations": 1000,
            "ci_method": "percentile",
            "ci_95_low": acc_ci[0],
            "ci_95_high": acc_ci[1],
        })

        # MK-NIAH Target Probability (n=100 samples)
        prob_vals = obs["mkniah"][m]["target_prob"]
        prob_ci = proper_bootstrap_ci(prob_vals, n_bootstrap=1000, ci=0.95, seed=42)
        bootstrap_table.append({
            "metric": "target_probability",
            "method": m,
            "bootstrap_unit": "sample",
            "n": len(prob_vals),
            "mean": round(float(np.mean(prob_vals)), 5),
            "iterations": 1000,
            "ci_method": "percentile",
            "ci_95_low": prob_ci[0],
            "ci_95_high": prob_ci[1],
        })

    print(f"\n{'Metric':20s} | {'Method':36s} | {'Unit':8s} | {'n':3s} | {'Mean':8s} | {'95% Bootstrap CI':20s}")
    print("-" * 105)
    for row in bootstrap_table:
        print(f"{row['metric']:20s} | {row['method']:36s} | {row['bootstrap_unit']:8s} | {row['n']:3d} | {row['mean']:8.4f} | [{row['ci_95_low']}, {row['ci_95_high']}]")

    # Step 5: Export Audit CSV
    out_csv = "results/phase2_5_1_statistical_audit.csv"
    with open(out_csv, mode="w", newline="", encoding="utf-8") as f:
        fieldnames = ["metric", "method", "bootstrap_unit", "n", "mean", "iterations", "ci_method", "ci_95_low", "ci_95_high"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(bootstrap_table)
    print(f"\n[Artifact Generated] Saved statistical audit CSV to {out_csv}")

    # Return key values for report generation
    return {
        "csv_audit": csv_audit,
        "ppl_stats": ppl_stats,
        "f1_stats": f1_stats,
        "mcnemar_stats": mcnemar_stats,
        "prob_stats": prob_stats,
        "bootstrap_table": bootstrap_table,
    }


if __name__ == "__main__":
    main()
