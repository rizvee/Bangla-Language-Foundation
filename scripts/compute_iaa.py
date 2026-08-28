#!/usr/bin/env python3
"""
BLF Dual-Target Inter-Annotator Agreement (IAA) Analyzer.

Computes rigorous dual IAA statistics over decoded human review records:
1. Candidate-Level Acceptability Agreement (Cohen's Kappa, Raw Agreement, Confusion Matrix, Category Breakdown)
2. Preferred-Candidate Set Agreement (Exact Matches, Partial Overlaps, Disjoint Sets)

Usage:
    python scripts/compute_iaa.py --input-decoded-a path/to/decoded_a.json --input-decoded-b path/to/decoded_b.json
    python scripts/compute_iaa.py --input-decoded-a path/to/decoded_a.json --input-decoded-b path/to/decoded_b.json --output-report report.json --output-disagreements disagreements.json
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from blf.quality.iaa import evaluate_dual_iaa


def load_records(path_str: str) -> List[Dict[str, Any]]:
    p = Path(path_str)
    if not p.is_file():
        raise FileNotFoundError(f"Decoded review file not found: {p}")
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, dict):
        return data.get("records", [])
    elif isinstance(data, list):
        return data
    return []


def main():
    parser = argparse.ArgumentParser(description="Compute dual-target IAA metrics across decoded review records.")
    parser.add_argument("--input-decoded-a", type=str, default=None, help="Path to decoded review JSON for Reviewer A")
    parser.add_argument("--input-decoded-b", type=str, default=None, help="Path to decoded review JSON for Reviewer B")
    parser.add_argument("--reviewer-a", type=str, default=None, help="Explicit Reviewer A pseudonym")
    parser.add_argument("--reviewer-b", type=str, default=None, help="Explicit Reviewer B pseudonym")
    parser.add_argument("--output-report", type=str, default=None, help="Path to save full JSON analysis report")
    parser.add_argument("--output-disagreements", type=str, default=None, help="Path to export flagged disagreements JSON")
    args = parser.parse_args()

    print("==================================================")
    print("BLF Dual-Target Inter-Annotator Agreement (IAA) Analyzer")
    print("==================================================")

    if not args.input_decoded_a or not args.input_decoded_b:
        print("INFO: Decoded review logs not specified.")
        print("Pairwise IAA engine is ready for decoded Stage 1 submissions.")
        print("CLI Syntax:")
        print("  python scripts/compute_iaa.py --input-decoded-a path/to/a.json --input-decoded-b path/to/b.json")
        sys.exit(0)

    records_a = load_records(args.input_decoded_a)
    records_b = load_records(args.input_decoded_b)

    rev_a = args.reviewer_a or (records_a[0].get("reviewer_pseudonym") if records_a else "REVIEWER_A")
    rev_b = args.reviewer_b or (records_b[0].get("reviewer_pseudonym") if records_b else "REVIEWER_B")

    results = evaluate_dual_iaa(records_a, records_b, rev_a, rev_b)

    print("--------------------------------------------------")
    print(f"Evaluated Pair: `{rev_a}` vs `{rev_b}`")
    print(f"Common Pilot Items Evaluated: {results['common_evaluated_items']}")
    if results['items_only_a']:
        print(f"  [WARN] Items evaluated only by {rev_a}: {len(results['items_only_a'])}")
    if results['items_only_b']:
        print(f"  [WARN] Items evaluated only by {rev_b}: {len(results['items_only_b'])}")
    print("--------------------------------------------------")
    print("TARGET A: CANDIDATE-LEVEL ACCEPTABILITY AGREEMENT")
    cand_res = results["candidate_acceptability"]
    print(f"  - Total Candidate Pairs:      {cand_res['total_candidate_pairs']}")
    print(f"  - Raw Percent Agreement:      {cand_res['raw_agreement'] * 100:.2f}%")
    print(f"  - Cohen's Kappa (κ):          {cand_res['cohens_kappa']:.3f}")
    print(f"  - Candidate Disagreements:    {cand_res['total_candidate_disagreements']}")
    print("  - Per-Category Breakdown:")
    for cat, stat in cand_res["category_breakdown"].items():
        print(f"      * {cat:22s}: {stat['agreed_count']}/{stat['candidate_pairs_count']} agreed ({stat['raw_agreement'] * 100:.1f}%)")
    print("--------------------------------------------------")
    print("TARGET B: PREFERRED-CANDIDATE SET AGREEMENT")
    pref_res = results["preferred_candidates"]
    print(f"  - Exact Set Matches:          {pref_res['exact_matches']}/{pref_res['total_items']} ({pref_res['exact_match_rate'] * 100:.1f}%)")
    print(f"  - Partial Overlaps:           {pref_res['partial_overlaps']}")
    print(f"  - Disjoint Preferences:       {pref_res['disjoint_preferences']}")
    print("==================================================")

    if args.output_report:
        out_r = Path(args.output_report)
        out_r.parent.mkdir(parents=True, exist_ok=True)
        with open(out_r, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"Saved full IAA analysis report -> {out_r}")

    if args.output_disagreements:
        out_d = Path(args.output_disagreements)
        out_d.parent.mkdir(parents=True, exist_ok=True)
        dis_payload = {
            "title": "BLF Disagreement Queue for Stage 2 Evidence-Aware Adjudication",
            "reviewer_a": rev_a,
            "reviewer_b": rev_b,
            "candidate_acceptability_disagreements": cand_res["disagreements"],
            "preference_disagreements": pref_res["disagreements"],
        }
        with open(out_d, "w", encoding="utf-8") as f:
            json.dump(dis_payload, f, ensure_ascii=False, indent=2)
        print(f"Saved flagged disagreements -> {out_d}")


if __name__ == "__main__":
    main()
