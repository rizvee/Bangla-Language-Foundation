#!/usr/bin/env python3
"""
BLF Sentence Families & Constrained Realization Validator.

Validates:
1. Diagnostic sentence families against schemas/v0_1/sentence_family.schema.json.
2. Referential integrity to semantic frames (FRAME-*) and constructions (CONST-*).
3. Human review invariants (no automated HUMAN_APPROVED).
4. Deterministic execution of ConstrainedRealizer.

Usage:
    python scripts/validate_sentence_families.py
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Add src to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from blf.validation.validators import load_schema, validate_dict_against_schema
from blf.generation.realizer import ConstrainedRealizer, RealizationError

SF_SCHEMA_PATH = ROOT_DIR / "schemas" / "v0_1" / "sentence_family.schema.json"
DIAGNOSTIC_PATH = ROOT_DIR / "data" / "validation" / "sentence_families_diagnostic.json"
FRAMES_PATH = ROOT_DIR / "ontology" / "frames" / "core_frames.json"
CONSTRUCTIONS_PATH = ROOT_DIR / "ontology" / "constructions" / "constructions.json"


def load_json(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_sentence_families() -> Tuple[int, int, List[str]]:
    errors = []
    total_families = 0

    schema = load_schema(SF_SCHEMA_PATH)
    sf_data = load_json(DIAGNOSTIC_PATH)
    frames_data = load_json(FRAMES_PATH)
    const_data = load_json(CONSTRUCTIONS_PATH)

    valid_frame_ids = {f["frame_id"] for f in frames_data.get("frames", [])}
    valid_const_ids = {c["construction_id"] for c in const_data.get("constructions", [])}
    families = sf_data.get("sentence_families", [])

    for sf in families:
        total_families += 1
        sf_id = sf.get("sentence_family_id", "UNKNOWN")

        # 1. Schema Conformance
        valid, schema_errs = validate_dict_against_schema(sf, schema)
        if not valid:
            errors.append(f"Sentence family schema violation in {sf_id}: {schema_errs}")

        # 2. Referential Integrity
        frame_id = sf.get("semantic_frame_id")
        if frame_id not in valid_frame_ids:
            errors.append(f"Sentence family {sf_id} references unknown semantic frame '{frame_id}'")

        prim_const = sf.get("primary_construction_id")
        if prim_const not in valid_const_ids:
            errors.append(f"Sentence family {sf_id} references unknown primary construction '{prim_const}'")

        # 3. Variants Construction References
        for v in sf.get("variants", []):
            cid = v.get("construction_id")
            if cid not in valid_const_ids:
                errors.append(f"Variant in {sf_id} references unknown construction '{cid}'")

        # 4. Anti-Automation Guardrail: No automated HUMAN_APPROVED
        if sf.get("human_review_status") == "HUMAN_APPROVED":
            errors.append(f"Guardrail violation in {sf_id}: Automated generation assigned 'HUMAN_APPROVED'")

    # 5. Programmatic Test of ConstrainedRealizer
    realizer = ConstrainedRealizer()
    
    # Transitive SOV
    res_tr = realizer.realize_transitive("সে", "বইটা", "পড়", "PRES_SIMP", "3_ORD")
    if res_tr != "সে বইটা পড়ে।":
        errors.append(f"Realizer failed transitive SOV: got '{res_tr}'")

    # Topicalized OSV
    res_top = realizer.realize_transitive("সে", "বইটা", "পড়", "PRES_SIMP", "3_ORD", is_topicalized=True)
    if res_top != "বইটা সে পড়ে।":
        errors.append(f"Realizer failed topicalized OSV: got '{res_top}'")

    # Invariant rejection test: Unsupported inverted stacked affixes
    try:
        realizer.check_morphotactic_invariants("কলমগুলোটি")
        errors.append("Realizer failed to reject unsupported inverted stacked affixes 'kolom-gulo-ti'")
    except RealizationError:
        pass

    return total_families, len(errors), errors


def main():
    print("==================================================")
    print("BLF Sentence Families & Constrained Realization Validator")
    print("==================================================")

    total, err_count, errors = validate_sentence_families()

    if errors:
        print(f"FAILED: {err_count} violation(s) found across {total} sentence families:")
        for err in errors:
            print(f"  - [FAIL] {err}")
        sys.exit(1)
    else:
        print(f"SUCCESS: All {total} sentence families and realization constraints are VALID.")
        sys.exit(0)


if __name__ == "__main__":
    main()
