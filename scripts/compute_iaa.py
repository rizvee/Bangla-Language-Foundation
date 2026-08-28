#!/usr/bin/env python3
"""
BLF Inter-Annotator Agreement (IAA) & Disagreement Queue Analyzer.

Evaluates multi-rater human review logs using explicit pairwise rater matching:
- Computes Cohen's Kappa, Raw Percent Agreement, and Confusion Matrices over the exact intersection.
- Generates detailed category breakdown reports.
- Exports flagged disagreement items for Stage 2 evidence-aware adjudication.

Usage:
    python scripts/compute_iaa.py --input-log path/to/reviews.json --reviewer-a REV-LINGUIST-01 --reviewer-b REV-NATIVE-02
    python scripts/compute_iaa.py --input-log path/to/reviews.json --reviewer-a REV-LINGUIST-01 --reviewer-b REV-NATIVE-02 --output-disagreements data/review_queue/disagreement_queue.json
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

from blf.quality.iaa import evaluate_reviewer_pair

CANONICAL_PILOT_PATH = ROOT_DIR / "data" / "review_queue" / "human_review_pilot_40.json"


def load_category_lookup() -> Dict[str, str]:
    if CANONICAL_PILOT_PATH.is_file():
        with open(CANONICAL_PILOT_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {it["pilot_id"]: it.get("category", "GENERAL") for it in data.get("items", [])}
    return {}


def main():
    parser = argparse.ArgumentParser(description="Compute rigorous pairwise IAA metrics for BLF human reviews.")
    parser.add_argument("--input-log", type=str, default=None, help="Path to human review decisions JSON file")
    parser.add_argument("--reviewer-a", type=str, default=None, help="First reviewer ID (e.g. REV-LINGUIST-01)")
    parser.add_argument("--reviewer-b", type=str, default=None, help="Second reviewer ID (e.g. REV-NATIVE-02)")
    parser.add_argument("--output-report", type=str, default=None, help="Path to write full IAA analysis report JSON")
    parser.add_argument("--output-disagreements", type=str, default=None, help="Path to export flagged disagreements JSON")
    args = parser.parse_args()

    print("==================================================")
    print("BLF Pairwise Inter-Annotator Agreement (IAA) Analyzer")
    print("==================================================")

    if not args.input_log:
        print("INFO: No active human review decision file provided.")
        print("Pairwise IAA engine is primed for Stage 1 pilot inputs.")
        print("Required CLI flags for active review logs:")
        print("  --input-log <file.json> --reviewer-a <REV_A> --reviewer-b <REV_B>")
        sys.exit(0)

    p = Path(args.input_log)
    if not p.is_file():
        print(f"ERROR: File not found: {p}", file=sys.stderr)
        sys.exit(1)

    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)

    reviews = data.get("reviews", []) if isinstance(data, dict) else data
    if not reviews:
        print("ERROR: No review records found in log.", file=sys.stderr)
        sys.exit(1)

    # Detect distinct reviewers in log
    distinct_reviewers = sorted(list({r.get("reviewer_id_pseudonymous") for r in reviews if r.get("reviewer_id_pseudonymous")}))
    print(f"Discovered {len(distinct_reviewers)} distinct reviewer(s) in log: {distinct_reviewers}")

    if not args.reviewer_a or not args.reviewer_b:
        if len(distinct_reviewers) == 2:
            rev_a = distinct_reviewers[0]
            rev_b = distinct_reviewers[1]
            print(f"Defaulting to detected rater pair: {rev_a} vs {rev_b}")
        else:
            print(f"ERROR: Log contains {len(distinct_reviewers)} reviewers. You must explicitly specify --reviewer-a and --reviewer-b.", file=sys.stderr)
            sys.exit(1)
    else:
        rev_a = args.reviewer_a
        rev_b = args.reviewer_b

    cat_lookup = load_category_lookup()
    results = evaluate_reviewer_pair(reviews, rev_a, rev_b, cat_lookup)

    print("--------------------------------------------------")
    print(f"Evaluated Pair: `{rev_a}` vs `{rev_b}`")
    print(f"Items Reviewed by {rev_a}: {results['total_items_reviewed_a']}")
    print(f"Items Reviewed by {rev_b}: {results['total_items_reviewed_b']}")
    print(f"Common Items Evaluated (Intersection): {results['common_evaluated_items']}")
    if results['items_only_a']:
        print(f"  [WARN] Items evaluated only by {rev_a}: {len(results['items_only_a'])}")
    if results['items_only_b']:
        print(f"  [WARN] Items evaluated only by {rev_b}: {len(results['items_only_b'])}")
    print("--------------------------------------------------")
    print(f"Raw Percent Agreement: {results['raw_agreement'] * 100:.2f}%")
    print(f"Cohen's Kappa (κ):     {results['cohens_kappa']:.3f}")
    print("--------------------------------------------------")
    print("Per-Category Breakdown:")
    for cat, stat in results["category_breakdown"].items():
        print(f"  - {cat:25s}: {stat['agreed_count']}/{stat['item_count']} agreed ({stat['raw_agreement'] * 100:.1f}%)")
    print("--------------------------------------------------")
    print(f"Flagged Disagreements for Stage 2 Adjudication: {results['total_disagreements']}")

    # Export report if requested
    if args.output_report:
        out_r = Path(args.output_report)
        out_r.parent.mkdir(parents=True, exist_ok=True)
        with open(out_r, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"Saved full analysis report -> {out_r}")

    # Export disagreements if requested
    if args.output_disagreements:
        out_d = Path(args.output_disagreements)
        out_d.parent.mkdir(parents=True, exist_ok=True)
        dis_payload = {
            "title": "BLF Disagreement Queue for Stage 2 Evidence-Aware Adjudication",
            "reviewer_a": rev_a,
            "reviewer_b": rev_b,
            "total_flagged_items": results["total_disagreements"],
            "disagreements": results["disagreement_items"],
        }
        with open(out_d, "w", encoding="utf-8") as f:
            json.dump(dis_payload, f, ensure_ascii=False, indent=2)
        print(f"Saved flagged disagreements -> {out_d}")

    print("==================================================")


if __name__ == "__main__":
    main()
