import json
from collections import Counter

with open("results/phase3_1_e2e_results.json", "r", encoding="utf-8") as f:
    data = json.load(f)

records = data["records"]
print(f"Total evaluations: {len(records)}")
print(f"Overall passed: {data['passed_evaluations']}/{len(records)} ({data['pass_rate']}%)")
print(f"Device: {data['device']}")
print(f"Model: {data['model']}")

print("\n--- By Mode ---")
mode_stats = {}
for i, r in enumerate(records):
    m = r.get("mode", "unknown")
    p = r.get("pass", r.get("passed", False))
    mode_stats.setdefault(m, {"total": 0, "pass": 0, "latencies": []})
    mode_stats[m]["total"] += 1
    if p:
        mode_stats[m]["pass"] += 1
    mode_stats[m]["latencies"].append(r.get("latency_ms", 0.0))

for m, s in mode_stats.items():
    avg_l = sum(s["latencies"]) / len(s["latencies"])
    rate = s["pass"] / s["total"] * 100
    print(f"Mode {m:10s}: {s['pass']:3d}/{s['total']:3d} ({rate:5.1f}%) | Avg Latency: {avg_l:8.2f} ms")

print("\n--- By Category ---")
cat_stats = {}
for r in records:
    c = r.get("category", "unknown")
    p = r.get("pass", r.get("passed", False))
    cat_stats.setdefault(c, {"total": 0, "pass": 0, "latencies": []})
    cat_stats[c]["total"] += 1
    if p:
        cat_stats[c]["pass"] += 1
    cat_stats[c]["latencies"].append(r.get("latency_ms", 0.0))

for c, s in cat_stats.items():
    avg_l = sum(s["latencies"]) / len(s["latencies"])
    rate = s["pass"] / s["total"] * 100
    print(f"Category {c:25s}: {s['pass']:3d}/{s['total']:3d} ({rate:5.1f}%) | Avg Latency: {avg_l:8.2f} ms")

print("\n--- By Category within Hybrid Mode (Task 10 Matrix: 100 questions) ---")
hybrid_cats = {}
for r in records:
    if r.get("mode") == "hybrid":
        c = r.get("category", "unknown")
        p = r.get("pass", r.get("passed", False))
        hybrid_cats.setdefault(c, {"total": 0, "pass": 0})
        hybrid_cats[c]["total"] += 1
        if p:
            hybrid_cats[c]["pass"] += 1

for c, s in hybrid_cats.items():
    rate = s["pass"] / s["total"] * 100
    print(f"Hybrid - {c:25s}: {s['pass']:3d}/{s['total']:3d} ({rate:5.1f}%)")

import csv
print("\n--- From CSV Rows ---")
with open("results/phase3_1_e2e_results.csv", "r", encoding="utf-8") as f:
    csv_rows = list(csv.DictReader(f))

by_mode_csv = {}
for r in csv_rows:
    m = r["Mode"]
    s = r["Status"]
    by_mode_csv.setdefault(m, {"PASS": 0, "FAIL": 0})
    by_mode_csv[m][s] += 1

for m, counts in by_mode_csv.items():
    tot = counts["PASS"] + counts["FAIL"]
    print(f"CSV Mode {m:10s}: PASS={counts['PASS']:3d}, FAIL={counts['FAIL']:3d} (Total {tot:3d})")

print("\n--- Citation Trace Statistics ---")
total_citations = 0
valid_traces = 0
for r in records:
    for tr in r.get("citation_traces", []):
        total_citations += 1
        if tr.get("valid"):
            valid_traces += 1
print(f"Total citations emitted: {total_citations}")
print(f"Valid traceable citations: {valid_traces} ({valid_traces/max(1, total_citations)*100:.1f}%)")

print("\n--- Memory Snapshot & Versioning Records ---")
print(json.dumps(data["memory_records"], indent=2))
