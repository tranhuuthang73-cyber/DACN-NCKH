"""
Phase 4.4 Automatic Result Ingestion Script
Organizes outputs into results/phase4_4/:
results/phase4_4/
├── A1/
├── A3/
├── RQ4/
├── checkpoints/
├── validation/
└── manifests/

Strictly preserves results/phase4_1/, results/phase4_2/, results/phase4_3/.
"""

import sys
import os
import shutil
import json
import argparse
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent.parent
RES_4_4 = ROOT_DIR / "results" / "phase4_4"

SUBDIRS = ["A1", "A3", "RQ4", "checkpoints", "validation", "manifests"]

def setup_ingestion_structure():
    for sub in SUBDIRS:
        (RES_4_4 / sub).mkdir(parents=True, exist_ok=True)
    print(f"[*] Ingestion directories initialized under {RES_4_4}")

def collect_results(dry_run=False):
    print("=" * 70)
    print("PHASE 4.4: AUTOMATIC RESULT INGESTION")
    print(f"Mode: {'DRY RUN' if dry_run else 'REAL INGESTION'}")
    print("=" * 70)

    setup_ingestion_structure()

    manifest = {
        "title": "Phase 4.4 Results Ingestion Manifest",
        "date": "2026-10-04",
        "dry_run": dry_run,
        "ingested_artifacts": {},
        "preserved_prior_phases": [
            "results/phase4_1/",
            "results/phase4_2/",
            "results/phase4_3/"
        ]
    }

    # 1. Ingestion plan / collection
    targets = {
        "A1": {
            "result_src": ROOT_DIR / "results" / "phase4_2" / "a1_external_results.json",
            "dest_dir": RES_4_4 / "A1",
            "ckpt_src_dir": ROOT_DIR / "checkpoints" / "phase4_2" / "A1"
        },
        "A3": {
            "result_src": ROOT_DIR / "results" / "phase4_2" / "a3_external_results.json",
            "dest_dir": RES_4_4 / "A3",
            "ckpt_src_dir": ROOT_DIR / "checkpoints" / "phase4_2" / "A3"
        },
        "RQ4": {
            "result_src": ROOT_DIR / "results" / "phase4_2" / "rq4_external_results.json",
            "dest_dir": RES_4_4 / "RQ4",
            "ckpt_src_dir": ROOT_DIR / "checkpoints" / "phase4_2" / "RQ4"
        }
    }

    for name, info in targets.items():
        if dry_run:
            manifest["ingested_artifacts"][name] = {
                "status": "AWAITING_EXTERNAL_GPU_RESULTS",
                "planned_source": str(info["result_src"].relative_to(ROOT_DIR)),
                "destination": str(info["dest_dir"].relative_to(ROOT_DIR))
            }
            print(f"    - [DRY RUN] {name}: Plan mapped -> {info['dest_dir'].name}/")
        else:
            if info["result_src"].exists():
                shutil.copy2(info["result_src"], info["dest_dir"] / info["result_src"].name)
                manifest["ingested_artifacts"][name] = {
                    "status": "INGESTED",
                    "file": info["result_src"].name
                }
                print(f"    - Ingested {name} results: {info['result_src'].name}")
            else:
                manifest["ingested_artifacts"][name] = {
                    "status": "NOT_FOUND_ON_DISK"
                }
                print(f"    - [WARNING] {name} results not found at {info['result_src']}")

    # Save manifest
    manifest_out = RES_4_4 / "manifests" / "ingestion_manifest.json"
    with open(manifest_out, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"[*] Ingestion manifest saved: {manifest_out}")
    print("[SUCCESS] Result Ingestion Process Finished.")
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Phase 4.4 Result Ingestion")
    parser.add_argument("--dry-run", action="store_true", help="Perform ingestion dry run")
    args = parser.parse_args()
    code = collect_results(dry_run=args.dry_run)
    sys.exit(code)
