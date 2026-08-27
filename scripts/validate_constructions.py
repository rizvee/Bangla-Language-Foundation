#!/usr/bin/env python3
"""
BLF Construction Grammar & Complex Predicates Validator.

Validates:
1. Construction catalog against schemas/v0_1/linguistic_construction.schema.json.
2. Complex predicate catalog against schemas/v0_1/complex_predicate.schema.json.
3. Referential integrity to atomic claims (CLM-*), rules (RUL-*), and examples (EX-*).
4. Deterministic execution of ComplexPredicateEngine.

Usage:
    python scripts/validate_constructions.py
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
from blf.linguistics.complex_predicates import ComplexPredicateEngine

CONST_SCHEMA_PATH = ROOT_DIR / "schemas" / "v0_1" / "linguistic_construction.schema.json"
CPRED_SCHEMA_PATH = ROOT_DIR / "schemas" / "v0_1" / "complex_predicate.schema.json"
CLAIMS_PATH = ROOT_DIR / "ontology" / "claims" / "pilot_claims.json"
RULES_PATH = ROOT_DIR / "ontology" / "rules" / "pilot_rules.json"
EXAMPLES_PATH = ROOT_DIR / "ontology" / "examples" / "pilot_examples.json"
CONSTRUCTIONS_PATH = ROOT_DIR / "ontology" / "constructions" / "constructions.json"
CPRED_PATH = ROOT_DIR / "ontology" / "complex_predicates" / "complex_predicates.json"


def load_json(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_constructions_and_predicates() -> Tuple[int, int, List[str]]:
    errors = []
    total_entities = 0

    const_schema = load_schema(CONST_SCHEMA_PATH)
    cpred_schema = load_schema(CPRED_SCHEMA_PATH)

    claims_data = load_json(CLAIMS_PATH)
    valid_claim_ids = {c["claim_id"] for c in claims_data.get("claims", [])}
    rules_data = load_json(RULES_PATH)
    valid_rule_ids = {r["rule_id"] for r in rules_data.get("rules", [])}
    examples_data = load_json(EXAMPLES_PATH)
    valid_example_ids = {e["example_id"] for e in examples_data.get("examples", [])}

    # 1. Validate Constructions
    if CONSTRUCTIONS_PATH.is_file():
        const_data = load_json(CONSTRUCTIONS_PATH)
        constructions = const_data.get("constructions", [])
        for c in constructions:
            total_entities += 1
            cid = c.get("construction_id", "UNKNOWN")

            valid, schema_errs = validate_dict_against_schema(c, const_schema)
            if not valid:
                errors.append(f"Construction schema violation in {cid}: {schema_errs}")

            for clm in c.get("supporting_claim_ids", []):
                if clm not in valid_claim_ids:
                    errors.append(f"Construction {cid} references unknown claim_id '{clm}'")

            for rul in c.get("supporting_rule_ids", []):
                if rul not in valid_rule_ids:
                    errors.append(f"Construction {cid} references unknown rule_id '{rul}'")

            for ex in c.get("example_ids", []):
                if ex not in valid_example_ids:
                    errors.append(f"Construction {cid} references unknown example_id '{ex}'")

    # 2. Validate Complex Predicates
    if CPRED_PATH.is_file():
        cpred_data = load_json(CPRED_PATH)
        predicates = cpred_data.get("complex_predicates", [])
        for cp in predicates:
            total_entities += 1
            pid = cp.get("predicate_id", "UNKNOWN")

            valid, schema_errs = validate_dict_against_schema(cp, cpred_schema)
            if not valid:
                errors.append(f"ComplexPredicate schema violation in {pid}: {schema_errs}")

            for clm in cp.get("supporting_claim_ids", []):
                if clm not in valid_claim_ids:
                    errors.append(f"ComplexPredicate {pid} references unknown claim_id '{clm}'")

    # 3. Test ComplexPredicateEngine Programmatically
    cp_engine = ComplexPredicateEngine()
    
    # Valid realization test
    res = cp_engine.realize_compound_verb("খা", "ফেলা", "PAST_SIMP.3_ORD")
    if res != "খেয়ে ফেলল":
        errors.append(f"ComplexPredicateEngine failed 'kheye phello' realization, got: '{res}'")

    # Selection restriction test
    valid_combo, msg = cp_engine.validate_vector_combination("খা", "ফেলা", "TRANSITIVE_DYNAMIC")
    if not valid_combo:
        errors.append(f"ComplexPredicateEngine falsely rejected valid combination: {msg}")

    invalid_combo, msg = cp_engine.validate_vector_combination("জান", "ফেলা", "STATIVE_COGNITION")
    if invalid_combo:
        errors.append("ComplexPredicateEngine failed to reject invalid stative combination with 'phela'")

    return total_entities, len(errors), errors


def main():
    print("==================================================")
    print("BLF Construction Grammar & Complex Predicates Validator")
    print("==================================================")

    total, err_count, errors = validate_constructions_and_predicates()

    if errors:
        print(f"FAILED: {err_count} violation(s) found across {total} entities:")
        for err in errors:
            print(f"  - [FAIL] {err}")
        sys.exit(1)
    else:
        print(f"SUCCESS: All {total} constructions and complex predicates are VALID.")
        sys.exit(0)


if __name__ == "__main__":
    main()
