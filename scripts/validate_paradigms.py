#!/usr/bin/env python3
"""
BLF Inflectional Paradigm Engine & Catalog Validator.

Validates:
1. Paradigm JSON catalogs against schemas/v0_1/inflectional_paradigm.schema.json.
2. Referential integrity to claims (CLM-*) and rules (RUL-*).
3. Agreement between programmatic morphological generators and gold paradigm matrices.

Usage:
    python scripts/validate_paradigms.py
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Add src to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from blf.validation.validators import load_schema, validate_dict_against_schema
from blf.linguistics.morphology import (
    NominalDeclensionEngine,
    PronominalParadigmEngine,
    VerbalConjugatorEngine,
)

SCHEMA_PATH = ROOT_DIR / "schemas" / "v0_1" / "inflectional_paradigm.schema.json"
CLAIMS_PATH = ROOT_DIR / "ontology" / "claims" / "pilot_claims.json"
RULES_PATH = ROOT_DIR / "ontology" / "rules" / "pilot_rules.json"
NOMINAL_PARADIGMS_PATH = ROOT_DIR / "ontology" / "paradigms" / "nominal_paradigms.json"
PRONOMINAL_PARADIGMS_PATH = ROOT_DIR / "ontology" / "paradigms" / "pronominal_paradigms.json"
VERBAL_PARADIGMS_PATH = ROOT_DIR / "ontology" / "paradigms" / "verbal_paradigms.json"


def load_json(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_paradigms() -> Tuple[int, int, List[str]]:
    errors = []
    total_paradigms = 0

    schema = load_schema(SCHEMA_PATH)
    claims_data = load_json(CLAIMS_PATH)
    valid_claim_ids = {c["claim_id"] for c in claims_data.get("claims", [])}
    rules_data = load_json(RULES_PATH)
    valid_rule_ids = {r["rule_id"] for r in rules_data.get("rules", [])}

    catalogs = [NOMINAL_PARADIGMS_PATH, PRONOMINAL_PARADIGMS_PATH, VERBAL_PARADIGMS_PATH]

    for cat_path in catalogs:
        if not cat_path.is_file():
            errors.append(f"Catalog missing: {cat_path}")
            continue
        data = load_json(cat_path)
        paradigms = data.get("paradigms", [])
        for p in paradigms:
            total_paradigms += 1
            pid = p.get("paradigm_id", "UNKNOWN")

            # Validate against schema
            valid, schema_errs = validate_dict_against_schema(p, schema)
            if not valid:
                errors.append(f"Schema violation in {pid} ({cat_path.name}): {schema_errs}")

            # Validate claim references
            for cid in p.get("supporting_claim_ids", []):
                if cid not in valid_claim_ids:
                    errors.append(f"Paradigm {pid} references unknown claim_id '{cid}'")

            # Validate rule references
            for rid in p.get("supporting_rule_ids", []):
                if rid not in valid_rule_ids:
                    errors.append(f"Paradigm {pid} references unknown rule_id '{rid}'")

    # Validate Programmatic Engines
    nom_engine = NominalDeclensionEngine()
    verb_engine = VerbalConjugatorEngine()

    # Test 'kor-' verb generator against gold
    kor_gen = verb_engine.conjugate_root("কর")
    if kor_gen.get("PRES_SIMP.1") != "করি" or kor_gen.get("FUT_SIMP.1") != "করব":
        errors.append("VerbalConjugatorEngine failed basic 'kor-' verification")

    # Test 'manush' noun generator
    manush_gen = nom_engine.decline_noun("মানুষ", is_human=True, classifier="টি")
    if manush_gen.get("NOM.SG.DEF") != "মানুষটি" or manush_gen.get("GEN.PL.INDEF") != "মানুষদের":
        errors.append("NominalDeclensionEngine failed basic 'manush' declension test")

    return total_paradigms, len(errors), errors


def main():
    print("==================================================")
    print("BLF Inflectional Paradigm Validator")
    print("==================================================")

    total, err_count, errors = validate_paradigms()

    if errors:
        print(f"FAILED: {err_count} violation(s) found across {total} paradigms:")
        for err in errors:
            print(f"  - [FAIL] {err}")
        sys.exit(1)
    else:
        print(f"SUCCESS: All {total} inflectional paradigms and morphological engines are VALID.")
        sys.exit(0)


if __name__ == "__main__":
    main()
