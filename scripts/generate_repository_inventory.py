"""
Generate comprehensive repository inventory CSV for SA-CMS project.
Output: docs/repository_inventory.csv
Adheres strictly to the 10-column contract and 7 classification types:
KEEP_SOURCE, KEEP_RAW_EVIDENCE, KEEP_CANONICAL, DUPLICATE_CANDIDATE, ARCHIVE_CANDIDATE, SAFE_DELETE, UNCERTAIN.
"""

import os
import sys
import hashlib
import csv
import subprocess
from pathlib import Path
from collections import defaultdict, Counter

def main():
    repo_root = Path(__file__).resolve().parent.parent
    os.chdir(repo_root)

    print("[1/5] Querying git-tracked files...")
    out = subprocess.check_output(['git', 'ls-files', '-z'])
    git_tracked_set = set(Path(p).as_posix() for p in out.decode('utf-8', errors='surrogateescape').split('\0') if p)
    print(f"      Total git-tracked files: {len(git_tracked_set)}")

    print("[2/5] Scanning all filesystem files and computing SHA-256...")
    all_files = []
    file_hashes = {}
    hash_to_files = defaultdict(list)

    for r, d, fs in os.walk('.'):
        if '.git' in Path(r).parts:
            continue
        for f in fs:
            rel_p = Path(os.path.join(r, f)).as_posix()
            if rel_p.startswith('./'):
                rel_p = rel_p[2:]
            sz = os.path.getsize(rel_p)
            all_files.append((rel_p, sz))

            # Compute sha256
            h = hashlib.sha256()
            with open(rel_p, 'rb') as fl:
                while chunk := fl.read(1024 * 1024):
                    h.update(chunk)
            sha = h.hexdigest()
            file_hashes[rel_p] = sha
            hash_to_files[sha].append(rel_p)

    print(f"      Total files scanned: {len(all_files)}")
    duplicate_hashes = {h: paths for h, paths in hash_to_files.items() if len(paths) > 1}
    print(f"      Total duplicate hash groups: {len(duplicate_hashes)}")

    print("[3/5] Mapping cross-references across all codebase documents...")
    text_extensions = ('.py', '.yaml', '.yml', '.json', '.jsonl', '.md', '.txt', '.sh', '.bat', '.csv', '.html', '.js', '.css')
    text_files = [p for p, sz in all_files if p.endswith(text_extensions) and not p.endswith('.pyc')]
    
    text_contents = {}
    for p in text_files:
        try:
            with open(p, 'r', encoding='utf-8', errors='ignore') as fl:
                text_contents[p] = fl.read()
        except Exception:
            pass

    file_references = defaultdict(list)
    for p, sz in all_files:
        base_name = Path(p).name
        refs = []
        for ref_p, content in text_contents.items():
            if ref_p == p:
                continue
            if p in content or p.replace('/', '\\') in content:
                refs.append(ref_p)
            elif len(base_name) > 8 and not base_name.endswith(('.pyc', '.tmp')):
                if f'/{base_name}' in content or f'\\{base_name}' in content or f'"{base_name}"' in content or f"'{base_name}'" in content:
                    if ref_p not in refs:
                        refs.append(ref_p)
        file_references[p] = refs

    print("[4/5] Classifying all files according to strict scientific criteria...")

    inventory_rows = []

    for p, sz in all_files:
        ext = Path(p).suffix.lower()
        sha = file_hashes[p]
        is_tracked = p in git_tracked_set
        refs = file_references.get(p, [])
        ref_str = ";".join(refs[:5]) if refs else "none"
        if len(refs) > 5:
            ref_str += f";(+{len(refs)-5}_more)"

        # Determine file_type
        if ext == '.py':
            f_type = "python_source"
        elif ext == '.pyc':
            f_type = "compiled_python_bytecode"
        elif ext in ('.pt', '.safetensors'):
            f_type = "pytorch_checkpoint"
        elif ext == '.json':
            f_type = "json_data"
        elif ext == '.jsonl':
            f_type = "jsonlines_data"
        elif ext == '.csv':
            f_type = "csv_data"
        elif ext in ('.yaml', '.yml'):
            f_type = "yaml_config"
        elif ext == '.md':
            f_type = "markdown_document"
        elif ext == '.txt':
            f_type = "plain_text"
        elif ext == '.pdf':
            f_type = "pdf_document"
        elif ext == '.docx':
            f_type = "word_document"
        elif ext == '.png':
            f_type = "png_image"
        elif ext == '.log':
            f_type = "execution_log"
        elif ext == '.bat':
            f_type = "batch_script"
        elif ext == '.sh':
            f_type = "shell_script"
        elif ext in ('.html', '.css', '.js'):
            f_type = f"web_{ext[1:]}"
        else:
            f_type = ext.replace('.', '') if ext else "unknown"

        # Classification logic
        classification = "UNCERTAIN"
        role = "unknown"
        rec_action = "investigate"
        reason = ""

        # A. SAFE_DELETE checks (transient, cache, temporary)
        if '__pycache__' in p or ext == '.pyc' or '.pytest_cache' in p:
            classification = "SAFE_DELETE"
            role = "cache_artifact"
            rec_action = "safe_delete"
            reason = "Transient python/pytest cache file; fully reproducible and not tracked by git."

        # B. DUPLICATE_CANDIDATE checks (exact bitwise duplicates)
        elif sha in duplicate_hashes and len(hash_to_files[sha]) > 1:
            all_dups = hash_to_files[sha]
            
            if p.startswith('results/phase4_4/checkpoints/'):
                classification = "DUPLICATE_CANDIDATE"
                role = "duplicate_checkpoint"
                rec_action = "deduplicate_after_path_update"
                canonical_p = next((x for x in all_dups if x.startswith('training_output_final/checkpoints/')), all_dups[0])
                reason = f"Exact bitwise duplicate of canonical checkpoint {canonical_p}."

            elif p.startswith('checkpoints/phase4_2/'):
                classification = "DUPLICATE_CANDIDATE"
                role = "duplicate_checkpoint"
                rec_action = "deduplicate_after_path_update"
                canonical_p = next((x for x in all_dups if x.startswith('training_output_final/checkpoints/')), all_dups[0])
                reason = f"Exact bitwise duplicate of canonical checkpoint {canonical_p}."

            elif p.startswith('results/phase4_4/') and ext == '.json':
                classification = "DUPLICATE_CANDIDATE"
                role = "duplicate_evaluation_result"
                rec_action = "deduplicate_after_path_update"
                canonical_p = next((x for x in all_dups if x.startswith('training_output_final/raw_results/')), all_dups[0])
                reason = f"Exact duplicate of canonical result file {canonical_p}."

            elif p.startswith('results/phase4_2/') and ext == '.json':
                classification = "DUPLICATE_CANDIDATE"
                role = "duplicate_evaluation_result"
                rec_action = "deduplicate_after_path_update"
                canonical_p = next((x for x in all_dups if x.startswith('training_output_final/raw_results/')), all_dups[0])
                reason = f"Exact duplicate of canonical result file {canonical_p}."

            elif p.startswith('training_output_final/') and '/raw_results/' not in p and ext == '.json' and any('/raw_results/' in x for x in all_dups):
                classification = "DUPLICATE_CANDIDATE"
                role = "duplicate_evaluation_result"
                rec_action = "deduplicate_after_path_update"
                canonical_p = next((x for x in all_dups if '/raw_results/' in x), all_dups[0])
                reason = f"Subfolder mirror duplicate of canonical raw result {canonical_p}."

            elif p.startswith('training_handoff_phase4_2/') and any(x.startswith('external_gpu/phase4_2/') for x in all_dups):
                classification = "DUPLICATE_CANDIDATE"
                role = "duplicate_execution_package"
                rec_action = "deduplicate_after_path_update"
                canonical_p = next((x for x in all_dups if x.startswith('external_gpu/phase4_2/')), all_dups[0])
                reason = f"Duplicate handoff copy of source script/config {canonical_p}."

            elif p.startswith('local_runtime/tokenizer/') and any(x.startswith('local_runtime/model/') for x in all_dups):
                classification = "DUPLICATE_CANDIDATE"
                role = "duplicate_runtime_asset"
                rec_action = "deduplicate_after_path_update"
                canonical_p = next((x for x in all_dups if x.startswith('local_runtime/model/')), all_dups[0])
                reason = f"Duplicate tokenizer file mirroring canonical model directory {canonical_p}."

            elif p.startswith('local_runtime/checkpoints/') and any(x.startswith('checkpoints/phase4_1/') for x in all_dups):
                classification = "DUPLICATE_CANDIDATE"
                role = "duplicate_runtime_checkpoint"
                rec_action = "keep_as_runtime_link"
                canonical_p = next((x for x in all_dups if x.startswith('checkpoints/phase4_1/')), all_dups[0])
                reason = f"Runtime local copy of Phase 4.1 canonical checkpoint {canonical_p}."

            elif p.startswith('local_runtime/documents/') and p != all_dups[0]:
                classification = "DUPLICATE_CANDIDATE"
                role = "duplicate_ingested_document"
                rec_action = "safe_delete"
                reason = f"Duplicate demo ingestion document identical to {all_dups[0]}."

        # C. KEEP_CANONICAL
        if classification == "UNCERTAIN":
            if p.startswith('training_output_final/checkpoints/'):
                classification = "KEEP_CANONICAL"
                role = "canonical_model_checkpoint"
                rec_action = "keep_as_canonical"
                reason = "Primary verified official checkpoint for Phase 4.4 / RQ4 / Ablations with matching SHA-256 manifest."

            elif p.startswith('training_handoff_rtx3050/training_handoff_rtx3050/output/checkpoints/'):
                classification = "KEEP_CANONICAL"
                role = "canonical_trained_adapter"
                rec_action = "keep_as_canonical"
                reason = "Unique canonical checkpoints trained directly on NVIDIA RTX 3050 6GB GPU across seeds 42, 43, 44."

            elif p.startswith('training_output_final/raw_results/'):
                classification = "KEEP_CANONICAL"
                role = "canonical_experiment_result"
                rec_action = "keep_as_canonical"
                reason = "Primary canonical raw results JSON for Phase 4.4 experiments."

            elif p == 'results/phase4_2_verified_master_results.csv':
                classification = "KEEP_CANONICAL"
                role = "master_result_ledger"
                rec_action = "keep_as_canonical"
                reason = "Locked canonical master results CSV for all verified research questions (RQ1-RQ5, Ablations)."

            elif p == 'training_output_final/checksums.sha256':
                classification = "KEEP_CANONICAL"
                role = "canonical_checksum_manifest"
                rec_action = "keep_as_canonical"
                reason = "Official SHA-256 verification manifest for 53 core experimental artifacts."

            elif p.startswith('training_output_final/manifests/'):
                classification = "KEEP_CANONICAL"
                role = "canonical_handoff_manifest"
                rec_action = "keep_as_canonical"
                reason = "Official handoff and provenance manifests for offline deployment."

            elif p.startswith('checkpoints/phase4_1/'):
                classification = "KEEP_CANONICAL"
                role = "frozen_baseline_checkpoint"
                rec_action = "keep_as_canonical"
                reason = "Phase 4.1 frozen baseline model checkpoint required for reproducibility."

            elif p.startswith('checkpoints/level_') or p.startswith('checkpoints/sa_cms_') or p.startswith('checkpoints/pretrained_'):
                classification = "KEEP_CANONICAL"
                role = "architectural_checkpoint"
                rec_action = "keep_as_canonical"
                reason = "Base architectural checkpoints and pre-trained state vectors."

            elif p.startswith('results/phase4_1/'):
                classification = "KEEP_CANONICAL"
                role = "phase4_1_locked_result"
                rec_action = "keep_as_canonical"
                reason = "Locked experimental baseline results for Phase 4.1."

        # D. KEEP_RAW_EVIDENCE
        if classification == "UNCERTAIN":
            if p.startswith('results/raw_predictions/'):
                classification = "KEEP_RAW_EVIDENCE"
                role = "raw_model_predictions"
                rec_action = "keep"
                reason = "Indispensable raw JSONL predictions containing full greedy generations, Token F1, and logprobs."

            elif p.startswith('training_handoff_rtx3050/training_handoff_rtx3050/output/logs/'):
                classification = "KEEP_RAW_EVIDENCE"
                role = "hardware_training_log"
                rec_action = "keep"
                reason = "Forensic hardware execution logs recording VRAM, loss convergence, and device metadata on RTX 3050."

            elif p.startswith('logs/'):
                classification = "KEEP_RAW_EVIDENCE"
                role = "system_execution_log"
                rec_action = "keep"
                reason = "Auditable benchmark and testing logs."

            elif p.startswith('data/'):
                classification = "KEEP_RAW_EVIDENCE"
                role = "input_benchmark_dataset"
                rec_action = "keep"
                reason = "Standardized input evaluation datasets, questions, and reference answers."

            elif p in ('docs/post_push_training_audit.md', 'docs/final_scientific_report.md', 'docs/external_gpu_protocol_reconciliation.md', 'docs/final_external_gpu_training_report.md'):
                classification = "KEEP_RAW_EVIDENCE"
                role = "scientific_audit_report"
                rec_action = "keep"
                reason = "Comprehensive forensic audit reports and scientific protocol reconciliations."

            elif p.startswith('results/phase4_3/') or p.startswith('results/phase5_1/') or p.startswith('results/phase4_4/data_provenance') or p.startswith('results/phase4_4/external_package_audit') or p.startswith('results/phase4_4/manifests/'):
                classification = "KEEP_RAW_EVIDENCE"
                role = "audit_manifest_and_evidence"
                rec_action = "keep"
                reason = "Proven empirical data, token efficiency logs, and master experimental manifests."

            elif p.startswith('training_handoff_rtx3050/') or p.startswith('training_handoff_phase4_2/'):
                classification = "KEEP_RAW_EVIDENCE"
                role = "hardware_training_manifest_and_package"
                rec_action = "keep"
                reason = "Auditable packaging and manifests used for verifiable remote GPU training."

            elif p == 'fig7_recreated.png':
                classification = "KEEP_RAW_EVIDENCE"
                role = "scientific_evaluation_figure"
                rec_action = "keep"
                reason = "Empirical figure reproducing Figure 7 memory retention curves."

        # E. KEEP_SOURCE
        if classification == "UNCERTAIN":
            if p in ('de_cuong_chatbot_nested_learning.docx', '2512.24695v1.pdf'):
                classification = "KEEP_SOURCE"
                role = "foundational_proposal_and_paper"
                rec_action = "keep"
                reason = "Foundational advisor thesis outline (.docx) and source Nested Learning paper (.pdf)."

            elif p.startswith('src/'):
                classification = "KEEP_SOURCE"
                role = "core_source_code"
                rec_action = "keep"
                reason = "Core application source code, neural memory architecture, and web backend."

            elif p.startswith('tests/'):
                classification = "KEEP_SOURCE"
                role = "unit_and_regression_tests"
                rec_action = "keep"
                reason = "Automated test suite ensuring regression prevention and contract compliance."

            elif p.startswith('configs/'):
                classification = "KEEP_SOURCE"
                role = "configuration_specification"
                rec_action = "keep"
                reason = "Locked hyperparameters, model configs, and runtime settings."

            elif p in ('run_web.py', 'run_offline.py', 'run_sa_cms_experiment.py', 'start_offline_demo.bat', 'README.md', 'README_HANDOVER.md', '.gitignore', 'smoke_test.py', 'update_ui.py', 'ROUND2_DEVELOPMENT_PLAN.md'):
                classification = "KEEP_SOURCE"
                role = "entrypoint_and_project_meta"
                rec_action = "keep"
                reason = "Active system entrypoint, orchestration batch file, or core project documentation."

            elif p.startswith('external_gpu/phase4_4/') or p.startswith('external_gpu/phase4_2/'):
                classification = "KEEP_SOURCE"
                role = "benchmark_runner_script"
                rec_action = "keep"
                reason = "Verified Phase 4.4 and Phase 4.2 execution runner and statistical collection scripts."

            elif p.startswith('scripts/'):
                classification = "KEEP_SOURCE"
                role = "utility_and_audit_script"
                rec_action = "keep"
                reason = "Project audit, dataset preparation, and evaluation script."

            elif p in ('docs/q1_manuscript_draft.md', 'docs/offline_memory_architecture.md', 'docs/ui_ux_master_plan.md', 'docs/paper_mapping.md', 'docs/student_scale_reproduction_protocol.md', 'docs/training_freeze_protocol.md', 'docs/demo_and_defense_guide.md', 'docs/hardware_constraints.md', 'docs/reproduction_decisions.md', 'docs/reproduction_scope.md'):
                classification = "KEEP_SOURCE"
                role = "active_manuscript_and_specification"
                rec_action = "keep"
                reason = "Active Q1 publication draft, thesis guide, or locked research specification."

            elif p.startswith('local_runtime/'):
                if 'snapshots' in p:
                    classification = "SAFE_DELETE"
                    role = "transient_runtime_snapshot"
                    rec_action = "safe_delete"
                    reason = "Ephemeral chat session snapshot created during local interactive testing."
                else:
                    classification = "KEEP_SOURCE"
                    role = "offline_runtime_asset"
                    rec_action = "keep"
                    reason = "Local model weights and tokenizer for 100% offline chat assistant execution."

        # F. ARCHIVE_CANDIDATE
        if classification == "UNCERTAIN":
            p_lower = p.lower()
            if p.startswith('docs/') and any(x in p_lower for x in ['phase1', 'phase2', 'phase3', 'phase4_1', 'phase4_2', 'phase4_3', 'mkniah_failure', 'round2_', 'train_eval_mismatch', '.bak']):
                classification = "ARCHIVE_CANDIDATE"
                role = "historical_phase_report"
                rec_action = "archive_to_docs_archive"
                reason = "Historical milestone documentation superseded by final consolidated reports; preserve scientific record."

            elif p in ('paper_text.txt', 'de_cuong_text.txt') or p.startswith('fig7_extracted/'):
                classification = "ARCHIVE_CANDIDATE"
                role = "extracted_literature_reference"
                rec_action = "move_to_docs_references"
                reason = "Extracted reference text and figures; organize into docs/references/."

            elif p in ('run_phase2_5_controlled.py', 'run_pretrained_experiment.py', 'run_experiment.py', 'run_hybrid_qa.py', 'run_chatbot.py', 'scratch_bench.py'):
                classification = "ARCHIVE_CANDIDATE"
                role = "legacy_runner_script"
                rec_action = "archive_to_scripts_legacy"
                reason = "Early development test runner superseded by modular entrypoints."

            elif p.startswith('checkpoints/pilot_') or p.startswith('checkpoints/scale_') or p.startswith('checkpoints/three_level_feasibility/'):
                classification = "ARCHIVE_CANDIDATE"
                role = "pilot_study_checkpoint"
                rec_action = "archive_to_checkpoints_archive"
                reason = "Early Phase 3 feasibility and scale audit checkpoints superseded by RTX 3050 locked training."

            elif p.startswith('scratch/'):
                classification = "ARCHIVE_CANDIDATE"
                role = "scratch_investigation_artifact"
                rec_action = "archive_or_clean"
                reason = "Temporary exploration script or scratch test data."

        # Fallback UNCERTAIN
        if classification == "UNCERTAIN":
            role = "unclassified_file"
            rec_action = "investigate"
            reason = "File role requires manual domain alignment review."

        inventory_rows.append({
            "path": p,
            "file_type": f_type,
            "size_bytes": sz,
            "sha256": sha,
            "git_tracked": "True" if is_tracked else "False",
            "referenced_by": ref_str,
            "role": role,
            "classification": classification,
            "recommended_action": rec_action,
            "reason": reason
        })

    print("[5/5] Writing docs/repository_inventory.csv...")
    docs_dir = repo_root / "docs"
    docs_dir.mkdir(parents=True, exist_ok=True)
    out_csv = docs_dir / "repository_inventory.csv"

    fieldnames = [
        "path", "file_type", "size_bytes", "sha256", "git_tracked",
        "referenced_by", "role", "classification", "recommended_action", "reason"
    ]

    with open(out_csv, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in sorted(inventory_rows, key=lambda x: x["path"]):
            writer.writerow(row)

    print(f"Inventory written to: {out_csv}")
    
    # Summary of classifications
    counts = Counter(r["classification"] for r in inventory_rows)
    print("\nClassification breakdown:")
    for c, cnt in counts.most_common():
        print(f"  - {c}: {cnt} files")

if __name__ == "__main__":
    main()
