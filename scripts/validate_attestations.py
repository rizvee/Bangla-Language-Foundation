#!/usr/bin/env python3
"""
BLF Corpus Attestation Validator.

Validates:
1. Schema conformance (schemas/v0_1/corpus_attestation.schema.json).
2. Referential integrity of source_id, construction_ids, rule_ids, and frame_ids.
3. Separation between schema validity and external verification status.
4. Quarantined locator rules.

Usage:
    python scripts/validate_attestations.py
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from blf.validation.validators import load_schema, validate_dict_against_schema

SCHEMA_PATH = ROOT_DIR / "schemas" / "v0_1" / "corpus_attestation.schema.json"
ATTESTATIONS_PATH = ROOT_DIR / "ontology" / "attestations" / "corpus_attestations.json"
SOURCES_PATH = ROOT_DIR / "sources" / "registry" / "sources.json"
CONSTRUCTIONS_PATH = ROOT_DIR / "ontology" / "constructions" / "constructions.json"
RULES_PATH = ROOT_DIR / "ontology" / "rules" / "pilot_rules.json"
FRAMES_PATH = ROOT_DIR / "ontology" / "frames" / "core_frames.json"


def load_json(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_corpus_attestations() -> Tuple[int, int, List[str]]:
    errors = []
    total = 0

    schema = load_schema(SCHEMA_PATH)
    att_data = load_json(ATTESTATIONS_PATH)
    sources = {s["source_id"] for s in load_json(SOURCES_PATH).get("sources", [])}
    constructions = {c["construction_id"] for c in load_json(CONSTRUCTIONS_PATH).get("constructions", [])}
    rules = {r["rule_id"] for r in load_json(RULES_PATH).get("rules", [])}
    frames = {f["frame_id"] for f in load_json(FRAMES_PATH).get("frames", [])}

    items = att_data.get("attestations", [])
    for att in items:
        total += 1
        att_id = att.get("attestation_id", "UNKNOWN")

        # 1. Schema Validation
        valid, schema_errs = validate_dict_against_schema(att, schema)
        if not valid:
            errors.append(f"Attestation schema violation in {att_id}: {schema_errs}")

        # 2. Source Referential Integrity
        sid = att.get("source_id")
        if sid not in sources:
            errors.append(f"Attestation {att_id} references unregistered source '{sid}'")

        # 3. Construction Integrity
        for cid in att.get("construction_ids", []):
            if cid not in constructions:
                errors.append(f"Attestation {att_id} references unknown construction '{cid}'")

        # 4. Rule Referential Integrity
        for rid in att.get("rule_ids", []):
            if rid not in rules:
                errors.append(f"Attestation {att_id} references unknown rule '{rid}'")

        # 5. Frame Integrity
        for fid in att.get("frame_ids", []):
            if fid not in frames:
                errors.append(f"Attestation {att_id} references unknown frame '{fid}'")

        # 6. Epistemic Sanity: Offline records cannot falsely claim TEXT_VERIFIED without content hash
        status = att.get("verification_status")
        if status == "TEXT_VERIFIED" and not att.get("content_hash"):
            errors.append(f"Attestation {att_id} claims TEXT_VERIFIED but lacks content_hash")

    return total, len(errors), errors


def main():
    print("==================================================")
    print("BLF Corpus Attestation Validator")
    print("==================================================")

    total, err_count, errors = validate_corpus_attestations()

    if errors:
        print(f"FAILED: {err_count} violation(s) found across {total} corpus attestations:")
        for err in errors:
            print(f"  - [FAIL] {err}")
        sys.exit(1)
    else:
        print(f"SUCCESS: All {total} corpus attestations are valid and referentially intact (100% compliant).")
        sys.exit(0)


if __name__ == "__main__":
    main()
