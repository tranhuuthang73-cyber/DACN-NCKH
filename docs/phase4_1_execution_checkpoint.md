# PHASE 4.1 BENCHMARK — EXECUTION STATE CHECKPOINT & RESUME GUIDE
**Date & Timestamp**: 2026-10-03 22:55:36 (UTC+7)  
**Status**: PAUSED SAFELY (Power outage / Battery protection)  
**System Hardware**: NVIDIA GeForce GTX 1650 Ti (4GB VRAM), Python 3.9.13, PyTorch 2.2.1+cu118  

---

## 1. Executive Summary of Progress

The Phase 4.1 Official Controlled Benchmark was safely halted upon user request due to a local power outage, ensuring zero file corruption, zero battery depletion, and zero data loss. All pre-requisite checkpoints and completed research question results are fully preserved and validated on disk.

| Component / Task | Status | Output File Location | Size / Detail |
| :--- | :---: | :--- | :--- |
| **Adapter Training (Exact 200 samples)** | **100% COMPLETE** | `checkpoints/phase4_1/cms_{1lvl,2lvl,3lvl}_seed_{42,43,44}.pt` | 9 checkpoints (100% trained & persistent) |
| **Phase 4.1A (RQ1 — Capacity Limit)** | **100% COMPLETE** | `results/phase4_1/rq1/rq1_raw_results.json` | 381 KB (QASPER, LongHealth, MK-NIAH across seeds 42, 43, 44) |
| **Phase 4.1B (RQ2 — Budget Match)** | **100% COMPLETE** | `results/phase4_1/rq2/rq2_raw_results.json` | 158 KB (Strictly matched $\Delta_{\text{events}} = 0$ across seeds 42, 43, 44) |
| **Phase 4.1C (RQ3 — Retention & Refusal)** | **IN PROGRESS (PAUSED)** | `logs/phase4_1_benchmark.log` | Seed 42: B1 & B2 evaluated. B5, P1, P2 and seeds 43, 44 pending |
| **Phase 4.1D (RQ4 — Continual Forgetting)** | **READY TO RUN** | `results/phase4_1/rq4/` | 20-document sequential stream evaluation ready |
| **Phase 4.1E (RQ5 — Overhead Profile)** | **READY TO RUN** | `results/phase4_1/rq5/` | Latency / peak VRAM / checkpoint size profiler ready |
| **Phase 4.1F (Vietnamese Final Benchmark)** | **READY TO RUN** | `results/phase4_1/vietnamese/` | 20 docs / 350 questions test set ready |

---

## 2. Partial Results Snapshot from RQ3 (Seed 42)

Before being halted, Phase 4.1C completed evaluating the first two baseline methods on the 100-question balanced test split (50 Answerable, 25 Unanswerable, 25 Insufficient Evidence):

* **Method B1 (ICL — Full Context):**
  * Token F1: `0.0050`
  * Faithfulness (Citation-supported rate): `0.0%`
  * Correct Refusal Rate: `0.0%`
  * False Refusal Rate: `0.0%`
  * *Observation*: Raw SmolLM2-135M suffers severe degradation in long-context Vietnamese without an external retrieval anchor and has no parametric mechanism to refuse unanswerable questions.
* **Method B2 (BM25 RAG — Calibrated CAND_07):**
  * Token F1: `0.1596` (Significant gain over B1)
  * Faithfulness (Citation-supported rate): `93.5%`
  * Correct Refusal Rate: `76.0%`
  * False Refusal Rate: `0.0%`
  * *Observation*: Calibrated evidence selection and refusal thresholds effectively ground model generation and accurately reject unsupported queries without falsely rejecting valid ones.

---

## 3. Resume Protocol for Tomorrow

When electricity is restored and the machine is securely plugged into AC power:

### Step 1: Launch the Main Runner
Open PowerShell in the workspace root and run:
```powershell
cd d:\NCKH
python scripts/run_phase4_1.py
```

### Automatic Resume Behavior:
1. `scripts/run_phase4_1.py` detects `results/phase4_1/rq1/rq1_raw_results.json` $\to$ **Skips RQ1 execution instantly**.
2. `scripts/run_phase4_1.py` detects `results/phase4_1/rq2/rq2_raw_results.json` $\to$ **Skips RQ2 execution instantly**.
3. `train_or_load_adapter` detects all `.pt` files in `checkpoints/phase4_1/` $\to$ **Loads trained adapters instantly without re-training**.
4. Execution seamlessly begins with **Phase 4.1C (RQ3)**, evaluates the remaining methods, and proceeds sequentially through **RQ4**, **RQ5**, and **Phase 4.1F (Vietnamese Benchmark)**.

---

### Step 2: Generate Final Statistical Reports & Tables
Once `run_phase4_1.py` completes, run the verified statistical aggregator:
```powershell
python scripts/aggregate_phase4_1_results.py
```
This automatically produces:
* `results/phase4_1_master_results.csv`
* `results/phase4_1_master_results.json`
* `docs/phase4_1_rq1.md`
* `docs/phase4_1_rq2.md`
* `docs/phase4_1_rq3.md`
* `docs/phase4_1_rq4.md`
* `docs/phase4_1_rq5.md`
* `docs/phase4_1_vietnamese.md`
* Non-parametric percentile bootstrap ($B=1000$) confidence intervals and paired Wilcoxon/t-test significance statistics comparing P1 vs B5 and P2 vs B2.

---

## 4. Verification Check
* Background task `task-2886`: Terminated.
* Process PID 77868: Terminated.
* GPU/VRAM: 0 MB allocated.
* All files safely synced to disk. Safe for machine shutdown.
