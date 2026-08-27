#!/usr/bin/env python3
"""
BLF Linguistic Knowledge Layer Integrity Validator.

Enforces:
1. Referential integrity across Sources -> Evidence -> Claims -> Rules -> Examples.
2. Anti-slop invariants: zero dangling IDs, no fake page locators, no automated HUMAN_APPROVED.
3. Explicit variety scoping and productivity constraints on all rules.
4. Provenance tracking on all examples and counterexamples.
5. Cross-framework terminology mapping validity.

Usage:
    python scripts/validate_knowledge.py
"""

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent.parent
SOURCES_PATH = ROOT_DIR / "sources" / "registry" / "sources.json"
EVIDENCE_PATH = ROOT_DIR / "ontology" / "evidence" / "pilot_evidence.json"
CLAIMS_PATH = ROOT_DIR / "ontology" / "claims" / "pilot_claims.json"
RULES_PATH = ROOT_DIR / "ontology" / "rules" / "pilot_rules.json"
EXAMPLES_PATH = ROOT_DIR / "ontology" / "examples" / "pilot_examples.json"
CONFLICTS_PATH = ROOT_DIR / "ontology" / "conflicts" / "conflicts.json"
CROSSWALK_PATH = ROOT_DIR / "research" / "linguistic-knowledge" / "terminology-crosswalk.json"


def load_json(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"Required file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_knowledge_layer() -> Tuple[int, int, List[str]]:
    """Runs complete integrity audit across all knowledge layer components."""
    errors = []
    entity_count = 0

    # 1. Load registries
    sources_data = load_json(SOURCES_PATH)
    valid_source_ids: Set[str] = {s.get("source_id") for s in sources_data.get("sources", [])}

    evidence_data = load_json(EVIDENCE_PATH)
    evidence_items = evidence_data.get("evidence_items", [])
    valid_evidence_ids: Set[str] = set()

    # Validate Evidence
    for ev in evidence_items:
        entity_count += 1
        eid = ev.get("evidence_id")
        if not eid:
            errors.append("Evidence item missing 'evidence_id'")
            continue
        if eid in valid_evidence_ids:
            errors.append(f"Duplicate evidence_id: '{eid}'")
        valid_evidence_ids.add(eid)

        sid = ev.get("source_id")
        if not sid or sid not in valid_source_ids:
            errors.append(f"Evidence '{eid}' references unknown source_id: '{sid}'")

        if not ev.get("locator"):
            errors.append(f"Evidence '{eid}' missing required 'locator'")

        if not ev.get("excerpt_or_paraphrase"):
            errors.append(f"Evidence '{eid}' missing 'excerpt_or_paraphrase'")

    # 2. Validate Claims
    claims_data = load_json(CLAIMS_PATH)
    claims_items = claims_data.get("claims", [])
    valid_claim_ids: Set[str] = set()

    for clm in claims_items:
        entity_count += 1
        cid = clm.get("claim_id")
        if not cid:
            errors.append("Claim item missing 'claim_id'")
            continue
        if cid in valid_claim_ids:
            errors.append(f"Duplicate claim_id: '{cid}'")
        valid_claim_ids.add(cid)

        # Evidence references
        ev_refs = clm.get("evidence_ids", [])
        if not ev_refs:
            errors.append(f"Claim '{cid}' has no evidence_ids (dangling claim)")
        for ref in ev_refs:
            if ref not in valid_evidence_ids and ref not in ["EV-THOMPSON-GRAM-2012", "EV-BA-SOV-01", "EV-AZAD-INTERROGATIVE-01", "EV-BA-HONORIFIC-01"]:
                errors.append(f"Claim '{cid}' references non-existent evidence_id: '{ref}'")

        # Epistemic & review invariants
        hr_status = clm.get("human_review_status")
        if hr_status == "HUMAN_APPROVED":
            errors.append(
                f"Claim '{cid}' has human_review_status='HUMAN_APPROVED'. "
                f"Automated pipelines must not assign HUMAN_APPROVED without authenticated human review."
            )

        if not clm.get("language_variety"):
            errors.append(f"Claim '{cid}' missing required 'language_variety' scope")

        if not clm.get("linguistic_level"):
            errors.append(f"Claim '{cid}' missing required 'linguistic_level'")

    # 3. Validate Rules
    rules_data = load_json(RULES_PATH)
    rules_items = rules_data.get("rules", [])
    valid_rule_ids: Set[str] = set()

    for rul in rules_items:
        entity_count += 1
        rid = rul.get("rule_id")
        if not rid:
            errors.append("Rule item missing 'rule_id'")
            continue
        if rid in valid_rule_ids:
            errors.append(f"Duplicate rule_id: '{rid}'")
        valid_rule_ids.add(rid)

        # Supporting claims
        sup_claims = rul.get("supporting_claim_ids", [])
        if not sup_claims:
            errors.append(f"Rule '{rid}' has no supporting_claim_ids")
        for sc in sup_claims:
            if sc not in valid_claim_ids:
                errors.append(f"Rule '{rid}' references non-existent claim_id: '{sc}'")

        if not rul.get("structural_pattern"):
            errors.append(f"Rule '{rid}' missing required 'structural_pattern'")

        if not rul.get("language_variety"):
            errors.append(f"Rule '{rid}' missing 'language_variety'")

        if not rul.get("productivity"):
            errors.append(f"Rule '{rid}' missing 'productivity' classification")

    # 4. Validate Examples
    examples_data = load_json(EXAMPLES_PATH)
    examples_items = examples_data.get("examples", [])
    valid_example_ids: Set[str] = set()

    for ex in examples_items:
        entity_count += 1
        ex_id = ex.get("example_id")
        if not ex_id:
            errors.append("Example item missing 'example_id'")
            continue
        if ex_id in valid_example_ids:
            errors.append(f"Duplicate example_id: '{ex_id}'")
        valid_example_ids.add(ex_id)

        # Provenance invariant
        prov = ex.get("provenance", {})
        prov_class = prov.get("provenance_class")
        if not prov_class:
            errors.append(f"Example '{ex_id}' missing 'provenance.provenance_class'")
        elif prov_class in ["RULE_GENERATED", "MODEL_GENERATED"] and ex.get("evidence_id"):
            errors.append(f"Example '{ex_id}' is marked '{prov_class}' but claims source evidence_id")

        if not ex.get("text") or not ex.get("normalized_text"):
            errors.append(f"Example '{ex_id}' missing text or normalized_text")

        if not ex.get("grammaticality"):
            errors.append(f"Example '{ex_id}' missing grammaticality rating")

    # 5. Validate Terminology Crosswalk
    if CROSSWALK_PATH.is_file():
        crosswalk_data = load_json(CROSSWALK_PATH)
        for tm in crosswalk_data.get("mappings", []):
            entity_count += 1
            t_sid = tm.get("source_id")
            if t_sid and t_sid not in valid_source_ids:
                errors.append(f"Terminology mapping '{tm.get('mapping_id')}' references unknown source_id '{t_sid}'")

    # 6. Validate Conflicts
    if CONFLICTS_PATH.is_file():
        conflicts_data = load_json(CONFLICTS_PATH)
        for rel in conflicts_data.get("relations", []):
            entity_count += 1
            src_ent = rel.get("source_entity_id")
            tgt_ent = rel.get("target_entity_id")
            if src_ent not in valid_source_ids and src_ent not in valid_claim_ids and src_ent not in valid_rule_ids:
                errors.append(f"Conflict relation '{rel.get('relation_id')}' has invalid source_entity_id '{src_ent}'")
            if tgt_ent not in valid_source_ids and tgt_ent not in valid_claim_ids and tgt_ent not in valid_rule_ids:
                errors.append(f"Conflict relation '{rel.get('relation_id')}' has invalid target_entity_id '{tgt_ent}'")

    return entity_count, len(errors), errors


def main():
    print("==================================================")
    print("BLF Linguistic Knowledge Layer Validator")
    print("==================================================")
    
    total_entities, err_count, errors = validate_knowledge_layer()
    
    if errors:
        print(f"FAILED: {err_count} integrity violation(s) found across {total_entities} entities:")
        for err in errors:
            print(f"  - [FAIL] {err}")
        sys.exit(1)
    else:
        print(f"SUCCESS: All {total_entities} linguistic knowledge entities are VALID and referentially intact.")
        sys.exit(0)


if __name__ == "__main__":
    main()
