#!/usr/bin/env python3
"""
BLF Review Submission Decoder.

Decodes raw blinded human submissions into internal canonical review records
using the private session mapping file.

Usage:
    python scripts/decode_review_submissions.py --session-mapping .blf-private/review_sessions/SESS-01/session_mapping.json --submission raw_sub.json --output-decoded decoded.json
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent.parent


def decode_submission(
    mapping_data: Dict[str, Any],
    submission_data: Dict[str, Any],
) -> List[Dict[str, Any]]:
    session_id = mapping_data.get("session_id")
    reviewer_id = submission_data.get("reviewer_pseudonym")
    submissions_list = submission_data.get("reviews", [submission_data]) if "reviews" in submission_data else [submission_data]

    rev_mappings = mapping_data.get("item_mappings", {}).get(reviewer_id, {})
    if not rev_mappings:
        raise ValueError(f"No item mappings found for reviewer '{reviewer_id}' in session mapping.")

    decoded_records = []
    now_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    for idx, sub in enumerate(submissions_list, start=1):
        opaque_id = sub["opaque_item_id"]
        if opaque_id not in rev_mappings:
            raise KeyError(f"Opaque item ID '{opaque_id}' not found in session mapping for reviewer '{reviewer_id}'.")

        map_info = rev_mappings[opaque_id]
        canonical_id = map_info["canonical_item_id"]
        category = map_info.get("category", "GENERAL")
        disp_to_can = map_info["displayed_to_canonical"]

        # Map candidate judgments
        raw_judgments = sub.get("candidate_judgments", {})
        canonical_judgments = {}
        for disp_lbl, j_val in raw_judgments.items():
            if disp_lbl in disp_to_can:
                can_id = disp_to_can[disp_lbl]
                canonical_judgments[can_id] = j_val

        # Map preferred candidates
        raw_prefs = sub.get("preferred_candidates", [])
        canonical_prefs = []
        for p in raw_prefs:
            if p == "NONE":
                canonical_prefs.append("NONE")
            elif p in disp_to_can:
                canonical_prefs.append(disp_to_can[p])

        decoded_record = {
            "decoded_record_id": f"DEC-REC-{reviewer_id}-{idx:04d}",
            "submission_id": sub.get("submission_id", f"REV-SUB-{idx:04d}"),
            "session_id": session_id,
            "reviewer_pseudonym": reviewer_id,
            "opaque_item_id": opaque_id,
            "canonical_item_id": canonical_id,
            "category": category,
            "displayed_to_canonical_mapping": disp_to_can,
            "canonical_candidate_judgments": canonical_judgments,
            "canonical_preferred_candidates": canonical_prefs,
            "correction": sub.get("correction"),
            "comments": sub.get("comments"),
            "decoded_timestamp": now_ts,
        }
        decoded_records.append(decoded_record)

    return decoded_records


def main():
    parser = argparse.ArgumentParser(description="Decode blinded human review submissions using session mappings.")
    parser.add_argument("--session-mapping", type=str, required=True, help="Path to session_mapping.json")
    parser.add_argument("--submission", type=str, required=True, help="Path to raw reviewer submission JSON")
    parser.add_argument("--output-decoded", type=str, required=True, help="Path to output decoded records JSON")
    args = parser.parse_args()

    with open(args.session_mapping, "r", encoding="utf-8") as f:
        mapping_data = json.load(f)

    with open(args.submission, "r", encoding="utf-8") as f:
        submission_data = json.load(f)

    decoded = decode_submission(mapping_data, submission_data)

    out_p = Path(args.output_decoded)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump({"title": "BLF Decoded Human Review Records", "total_records": len(decoded), "records": decoded}, f, ensure_ascii=False, indent=2)

    print(f"Decoded {len(decoded)} submission records -> {out_p}")


if __name__ == "__main__":
    main()
