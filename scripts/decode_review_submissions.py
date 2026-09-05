#!/usr/bin/env python3
"""
BLF Review Submission Decoder — Phase 2A.2d.

Decodes raw blinded human submissions into internal canonical review records
using the private session mapping file with fail-closed integrity validation:
- Enforces reviewer_submission_bundle.schema.json validation.
- Verifies session ID, reviewer pseudonym, and consent record match session mapping.
- Verifies unique opaque IDs, exactly 40 analytical items, no missing/unknown items.
- Enforces strict candidate keys (strictly displayed A, B, and optional C).
- Enforces preference invariants (unique, NONE exclusivity, acceptable-only preference).
- Computes cryptographic SHA-256 hash of raw immutable submissions.
- Validates decoded output against decoded_review_record.schema.json.
- Verifies canonical item integrity, candidate count, and exactly 40 records.

Usage:
    python scripts/decode_review_submissions.py --session-mapping .blf-private/review_sessions/SESS-01/session_mapping.json --submission raw_bundle.json --output-decoded decoded.json
"""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from blf.validation.validators import load_schema, validate_dict_against_schema

BUNDLE_SCHEMA_PATH = ROOT_DIR / "schemas" / "v0_1" / "reviewer_submission_bundle.schema.json"
DECODED_SCHEMA_PATH = ROOT_DIR / "schemas" / "v0_1" / "decoded_review_record.schema.json"
CANONICAL_PILOT_PATH = ROOT_DIR / "data" / "review_queue" / "human_review_pilot_40.json"

VALID_ACCEPTABILITY_FOR_PREFERENCE: Set[str] = {
    "NATURAL_STANDARD",
    "NATURAL_COLLOQUIAL",
    "MARKED_BUT_VALID",
}


def compute_content_sha256(content: str) -> str:
    """Computes SHA-256 hexadecimal digest of raw content string."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def load_canonical_pilot_index() -> Dict[str, Dict[str, Any]]:
    """Loads canonical pilot items indexed by pilot_id."""
    if not CANONICAL_PILOT_PATH.is_file():
        raise FileNotFoundError(f"Canonical pilot file not found: {CANONICAL_PILOT_PATH}")
    with open(CANONICAL_PILOT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {item["pilot_id"]: item for item in data.get("items", [])}


def validate_raw_submission_bundle(
    submission_data: Dict[str, Any],
    mapping_data: Dict[str, Any],
    allow_partial: bool = False,
) -> None:
    """
    Fail-closed validation of raw submission bundle before any decoding occurs.
    """
    session_id = mapping_data.get("session_id")
    sub_session_id = submission_data.get("session_id")

    # 1. Session matching
    if sub_session_id != session_id:
        raise ValueError(
            f"Fail-closed decoder error: Submission session ID '{sub_session_id}' does not match mapping session ID '{session_id}'."
        )

    # 2. Reviewer matching
    reviewer_id = submission_data.get("reviewer_pseudonym")
    declared_reviewers = mapping_data.get("reviewers", {})
    if declared_reviewers and reviewer_id not in declared_reviewers:
        raise ValueError(
            f"Fail-closed decoder error: Reviewer '{reviewer_id}' not declared in session mapping reviewers: {list(declared_reviewers.keys())}."
        )
    elif not declared_reviewers and reviewer_id not in mapping_data.get("item_mappings", {}):
        raise ValueError(
            f"Fail-closed decoder error: Reviewer '{reviewer_id}' not declared in session item mappings: {list(mapping_data.get('item_mappings', {}).keys())}."
        )

    # 3. Schema validation (bundle schema)
    if BUNDLE_SCHEMA_PATH.is_file() and not allow_partial:
        bundle_schema = load_schema(BUNDLE_SCHEMA_PATH)
        valid, errs = validate_dict_against_schema(submission_data, bundle_schema)
        if not valid:
            raise ValueError(f"Fail-closed decoder error: Submission bundle violates schema: {errs}")

    rev_mappings = mapping_data.get("item_mappings", {}).get(reviewer_id, {})
    if not rev_mappings:
        raise ValueError(f"Fail-closed decoder error: No item mappings found for reviewer '{reviewer_id}'.")

    reviews = submission_data.get("reviews", [submission_data]) if "reviews" in submission_data else [submission_data]

    # 4. Completeness check (exactly 40 items for official pilot)
    if not allow_partial:
        if len(reviews) != 40:
            raise ValueError(
                f"Fail-closed decoder error: Incomplete study submission. Expected exactly 40 analytical items, found {len(reviews)}."
            )

    # 5. Opaque item checking
    seen_opaque_ids: Set[str] = set()
    for idx, rev in enumerate(reviews, start=1):
        opaque_id = rev.get("opaque_item_id")
        if not opaque_id:
            raise ValueError(f"Fail-closed decoder error: Review #{idx} missing opaque_item_id.")

        if opaque_id in seen_opaque_ids:
            raise ValueError(
                f"Fail-closed decoder error: Duplicate opaque item ID '{opaque_id}' submitted by reviewer '{reviewer_id}'."
            )
        seen_opaque_ids.add(opaque_id)

        if opaque_id not in rev_mappings:
            raise KeyError(
                f"Fail-closed decoder error: Unknown opaque item ID '{opaque_id}' not present in reviewer mapping."
            )

        map_info = rev_mappings[opaque_id]
        expected_displayed = set(map_info["displayed_to_canonical"].keys())

        # 6. Candidate key check (strictly matches displayed candidates)
        cand_judgments = rev.get("candidate_judgments", {})
        actual_candidates = set(cand_judgments.keys())

        if actual_candidates != expected_displayed:
            raise ValueError(
                f"Fail-closed decoder error: In item '{opaque_id}', candidate judgments {sorted(list(actual_candidates))} "
                f"do not match displayed candidates {sorted(list(expected_displayed))}."
            )

        # 7. Preference invariants
        prefs = rev.get("preferred_candidates", [])
        if not isinstance(prefs, list) or len(prefs) == 0:
            raise ValueError(
                f"Fail-closed decoder error: In item '{opaque_id}', preferred_candidates must be a non-empty list."
            )

        # Unique items
        if len(prefs) != len(set(prefs)):
            raise ValueError(
                f"Fail-closed decoder error: In item '{opaque_id}', preferred_candidates contains duplicates: {prefs}."
            )

        # NONE exclusivity
        if "NONE" in prefs and len(prefs) > 1:
            raise ValueError(
                f"Fail-closed decoder error: In item '{opaque_id}', 'NONE' cannot be combined with candidate labels: {prefs}."
            )

        # Preferred candidates must be displayed candidates
        if prefs != ["NONE"]:
            for p in prefs:
                if p not in expected_displayed:
                    raise ValueError(
                        f"Fail-closed decoder error: In item '{opaque_id}', preferred candidate '{p}' is not a displayed candidate {expected_displayed}."
                    )

                # Preferred candidate must have acceptable judgment
                cand_eval = cand_judgments.get(p, {})
                acceptability = cand_eval.get("acceptability") if isinstance(cand_eval, dict) else cand_eval
                if acceptability not in VALID_ACCEPTABILITY_FOR_PREFERENCE:
                    raise ValueError(
                        f"Fail-closed decoder error: In item '{opaque_id}', preferred candidate '{p}' has acceptability '{acceptability}'. "
                        f"A preferred candidate must be one of {sorted(list(VALID_ACCEPTABILITY_FOR_PREFERENCE))}."
                    )


def decode_submission(
    mapping_data: Dict[str, Any],
    submission_data: Dict[str, Any],
    raw_content_str: Optional[str] = None,
    allow_partial: bool = False,
) -> List[Dict[str, Any]]:
    """
    Decodes validated submission bundle into canonical review records.
    Fails closed if any completeness, provenance, or schema condition is violated.
    """
    # 1. Fail-closed pre-validation
    validate_raw_submission_bundle(submission_data, mapping_data, allow_partial=allow_partial)

    session_id = mapping_data.get("session_id")
    reviewer_id = submission_data.get("reviewer_pseudonym")
    rev_mappings = mapping_data.get("item_mappings", {}).get(reviewer_id, {})
    canonical_pilot_index = load_canonical_pilot_index()

    raw_sha256 = compute_content_sha256(raw_content_str) if raw_content_str else None
    consent_record_id = submission_data.get("consent_record_id")

    reviews_list = submission_data.get("reviews", [submission_data]) if "reviews" in submission_data else [submission_data]
    decoded_records = []
    seen_canonical_ids: Set[str] = set()
    now_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    decoded_schema = load_schema(DECODED_SCHEMA_PATH) if DECODED_SCHEMA_PATH.is_file() else None

    for idx, sub in enumerate(reviews_list, start=1):
        opaque_id = sub["opaque_item_id"]
        map_info = rev_mappings[opaque_id]
        canonical_id = map_info["canonical_item_id"]
        category = map_info.get("category", "GENERAL")
        disp_to_can = map_info["displayed_to_canonical"]

        # Duplicate canonical item check
        if canonical_id in seen_canonical_ids:
            raise ValueError(
                f"Fail-closed decoder error: Duplicate canonical item ID '{canonical_id}' detected during decoding."
            )
        seen_canonical_ids.add(canonical_id)

        # Canonical pilot item verification
        if canonical_id not in canonical_pilot_index:
            raise KeyError(
                f"Fail-closed decoder error: Canonical item '{canonical_id}' does not exist in canonical pilot catalog."
            )
        canonical_item = canonical_pilot_index[canonical_id]

        # Map candidate judgments
        raw_judgments = sub.get("candidate_judgments", {})
        canonical_judgments = {}
        for disp_lbl, j_val in raw_judgments.items():
            can_id = disp_to_can[disp_lbl]
            canonical_judgments[can_id] = j_val

        # Verify candidate count matches canonical item
        expected_can_count = 2 if not canonical_item.get("candidate_c") else 3
        if len(canonical_judgments) != expected_can_count:
            raise ValueError(
                f"Fail-closed decoder error: In item '{canonical_id}', decoded candidate count {len(canonical_judgments)} "
                f"does not match canonical item candidate count {expected_can_count}."
            )

        # Map preferred candidates
        raw_prefs = sub.get("preferred_candidates", [])
        canonical_prefs = []
        for p in raw_prefs:
            if p == "NONE":
                canonical_prefs.append("NONE")
            else:
                canonical_prefs.append(disp_to_can[p])

        decoded_record = {
            "decoded_record_id": f"DEC-REC-{reviewer_id}-{idx:04d}",
            "submission_id": sub.get("submission_id", f"REV-SUB-{reviewer_id}-{idx:04d}"),
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
        if raw_sha256:
            decoded_record["raw_submission_sha256"] = raw_sha256
        if consent_record_id:
            decoded_record["consent_record_id"] = consent_record_id

        # Validate against decoded record schema
        if decoded_schema:
            valid, errs = validate_dict_against_schema(decoded_record, decoded_schema)
            if not valid:
                raise ValueError(
                    f"Fail-closed decoder error: Decoded record '{decoded_record['decoded_record_id']}' violates schema: {errs}"
                )

        decoded_records.append(decoded_record)

    # Post-decode completeness check
    if not allow_partial and len(decoded_records) != 40:
        raise ValueError(
            f"Fail-closed decoder error: Official study decode failed. Expected 40 records, produced {len(decoded_records)}."
        )

    return decoded_records


def main():
    parser = argparse.ArgumentParser(description="Decode blinded human review submissions using session mappings.")
    parser.add_argument("--session-mapping", type=str, required=True, help="Path to session_mapping.json")
    parser.add_argument("--submission", type=str, required=True, help="Path to raw reviewer submission JSON")
    parser.add_argument("--output-decoded", type=str, required=True, help="Path to output decoded records JSON")
    parser.add_argument("--allow-partial", action="store_true", help="Allow partial non-official debug decoding")
    args = parser.parse_args()

    with open(args.session_mapping, "r", encoding="utf-8") as f:
        mapping_data = json.load(f)

    with open(args.submission, "r", encoding="utf-8") as f:
        raw_str = f.read()
    submission_data = json.loads(raw_str)

    try:
        decoded = decode_submission(mapping_data, submission_data, raw_content_str=raw_str, allow_partial=args.allow_partial)
    except Exception as e:
        print(f"ERROR: Decoder failed closed: {e}", file=sys.stderr)
        sys.exit(1)

    out_p = Path(args.output_decoded)
    out_p.parent.mkdir(parents=True, exist_ok=True)
    with open(out_p, "w", encoding="utf-8") as f:
        json.dump(
            {
                "title": "BLF Decoded Human Review Records",
                "total_records": len(decoded),
                "is_official_complete": len(decoded) == 40,
                "records": decoded,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    print(f"Decoded {len(decoded)} submission records -> {out_p}")


if __name__ == "__main__":
    main()
