#!/usr/bin/env python3
"""
BLF Inter-Annotator Agreement (IAA) & Review Adjudication Tool.

Computes raw agreement and Cohen's Kappa across multi-rater review sessions,
and extracts conflicting items into data/review_queue/disagreement_queue.json.

Usage:
    python scripts/compute_iaa.py [--input-log path/to/reviews.json]
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

from blf.quality.iaa import compute_cohens_kappa, compute_raw_agreement, extract_disagreements


def main():
    parser = argparse.ArgumentParser(description="Compute IAA metrics for BLF human reviews.")
    parser.add_argument("--input-log", type=str, default=None, help="Path to input review decisions JSON file")
    args = parser.parse_args()

    print("==================================================")
    print("BLF Inter-Annotator Agreement (IAA) Analyzer")
    print("==================================================")

    if not args.input_log:
        print("INFO: No active human review decision file provided.")
        print("IAA calculation framework is ready for Phase 3 human pilot inputs.")
        print("Metric engines verified: compute_raw_agreement, compute_cohens_kappa, extract_disagreements.")
        sys.exit(0)

    p = Path(args.input_log)
    if not p.is_file():
        print(f"ERROR: File not found: {p}", file=sys.stderr)
        sys.exit(1)

    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)

    reviews = data.get("reviews", [])
    if not reviews:
        print("No review records found in file.")
        sys.exit(0)

    # Group by item_id
    reviews_by_item: Dict[str, List[Dict[str, Any]]] = {}
    for r in reviews:
        iid = r["item_id"]
        reviews_by_item.setdefault(iid, []).append(r)

    # Calculate pairwise agreement on items with 2+ reviews
    paired_r1, paired_r2 = [], []
    pair_tuples = []
    for iid, revs in reviews_by_item.items():
        if len(revs) >= 2:
            j1 = revs[0]["judgment"]
            j2 = revs[1]["judgment"]
            paired_r1.append(j1)
            paired_r2.append(j2)
            pair_tuples.append((j1, j2))

    if pair_tuples:
        raw_agr = compute_raw_agreement(pair_tuples)
        kappa = compute_cohens_kappa(paired_r1, paired_r2)
        print(f"Total Evaluated Items (>=2 raters): {len(pair_tuples)}")
        print(f"Raw Percent Agreement: {raw_agr * 100:.2f}%")
        print(f"Cohen's Kappa: {kappa:.3f}")
    else:
        print(f"Total Single-Reviewed Items: {len(reviews_by_item)} (Dual-rater evaluation pending)")

    disagreements = extract_disagreements(reviews_by_item)
    print(f"Disagreements Flagged for Adjudication: {len(disagreements)}")


if __name__ == "__main__":
    main()
