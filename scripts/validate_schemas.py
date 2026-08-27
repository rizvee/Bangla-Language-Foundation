#!/usr/bin/env python3
"""
Validates all JSON schema definitions and sample test fixtures in BLF.
"""

import sys
import json
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add src to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from blf.validation.validators import load_schema, validate_dict_against_schema


def main():
    root_dir = Path(__file__).parent.parent
    schemas_dir = root_dir / "schemas" / "v0_1"
    fixtures_dir = root_dir / "data" / "validation" / "fixtures"

    schema_files = list(schemas_dir.glob("*.json"))
    if not schema_files:
        print(f"No schema files found in {schemas_dir}")
        sys.exit(1)

    print(f"Validating {len(schema_files)} JSON schema file(s)...")
    has_errors = False

    for s_path in schema_files:
        try:
            schema = load_schema(s_path)
            print(f"  [OK] {s_path.name}: Valid JSON syntax (ID: {schema.get('$id', 'N/A')})")
        except Exception as e:
            print(f"  [ERROR] {s_path.name}: {e}")
            has_errors = True

    # Validate test fixtures if present
    if fixtures_dir.exists():
        fixture_files = list(fixtures_dir.glob("*.json"))
        if fixture_files:
            print(f"\nValidating {len(fixture_files)} test fixture(s)...")
            utterance_schema = load_schema(schemas_dir / "utterance.schema.json")
            for f_path in fixture_files:
                try:
                    with open(f_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    valid, errors = validate_dict_against_schema(data, utterance_schema)
                    if valid:
                        print(f"  [OK] {f_path.name}: Valid against utterance schema")
                    else:
                        print(f"  [FAIL] {f_path.name}: {errors}")
                        has_errors = True
                except Exception as e:
                    print(f"  [ERROR] {f_path.name}: {e}")
                    has_errors = True

    # Validate ontology instances against linguistic schemas
    ontology_mappings = [
        (root_dir / "ontology" / "evidence" / "pilot_evidence.json", "evidence_items", schemas_dir / "linguistic_evidence.schema.json"),
        (root_dir / "ontology" / "claims" / "pilot_claims.json", "claims", schemas_dir / "linguistic_claim.schema.json"),
        (root_dir / "ontology" / "rules" / "pilot_rules.json", "rules", schemas_dir / "linguistic_rule.schema.json"),
        (root_dir / "ontology" / "examples" / "pilot_examples.json", "examples", schemas_dir / "linguistic_example.schema.json"),
        (root_dir / "ontology" / "paradigms" / "nominal_paradigms.json", "paradigms", schemas_dir / "inflectional_paradigm.schema.json"),
        (root_dir / "ontology" / "paradigms" / "pronominal_paradigms.json", "paradigms", schemas_dir / "inflectional_paradigm.schema.json"),
        (root_dir / "ontology" / "paradigms" / "verbal_paradigms.json", "paradigms", schemas_dir / "inflectional_paradigm.schema.json"),
        (root_dir / "ontology" / "constructions" / "constructions.json", "constructions", schemas_dir / "linguistic_construction.schema.json"),
        (root_dir / "ontology" / "complex_predicates" / "complex_predicates.json", "complex_predicates", schemas_dir / "complex_predicate.schema.json"),
        (root_dir / "ontology" / "pragmatics" / "dialogue_acts.json", "dialogue_acts", schemas_dir / "dialogue_act.schema.json"),
    ]

    print("\nValidating ontology instances against JSON schemas...")
    for data_path, key_name, schema_path in ontology_mappings:
        if data_path.is_file() and schema_path.is_file():
            try:
                schema = load_schema(schema_path)
                with open(data_path, "r", encoding="utf-8") as f:
                    container = json.load(f)
                items = container.get(key_name, [])
                item_errors = []
                for item in items:
                    valid, errors = validate_dict_against_schema(item, schema)
                    if not valid:
                        item_errors.append(f"Item {item.get(list(item.keys())[0], 'N/A')}: {errors}")
                if item_errors:
                    print(f"  [FAIL] {data_path.name} ({len(item_errors)} errors):")
                    for ie in item_errors:
                        print(f"    - {ie}")
                    has_errors = True
                else:
                    print(f"  [OK] {data_path.name}: All {len(items)} items valid against {schema_path.name}")
            except Exception as e:
                print(f"  [ERROR] {data_path.name}: {e}")
                has_errors = True

    print("\n" + "=" * 50)
    if has_errors:
        print("Schema validation FAILED.")
        sys.exit(1)
    else:
        print("All schemas and fixtures are VALID.")
        sys.exit(0)


if __name__ == "__main__":
    main()
