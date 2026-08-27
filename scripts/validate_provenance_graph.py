#!/usr/bin/env python3
"""
BLF Provenance Graph Integrity Validator.

Verifies complete backward derivation tracing:
SentenceFamily -> SemanticFrame -> Construction -> Rule -> Claim -> Evidence -> Source

Usage:
    python scripts/validate_provenance_graph.py
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

SOURCES_PATH = ROOT_DIR / "sources" / "registry" / "sources.json"
EVIDENCE_PATH = ROOT_DIR / "ontology" / "evidence" / "pilot_evidence.json"
CLAIMS_PATH = ROOT_DIR / "ontology" / "claims" / "pilot_claims.json"
RULES_PATH = ROOT_DIR / "ontology" / "rules" / "pilot_rules.json"
CONSTRUCTIONS_PATH = ROOT_DIR / "ontology" / "constructions" / "constructions.json"
FRAMES_PATH = ROOT_DIR / "ontology" / "frames" / "core_frames.json"
FAMILIES_PATH = ROOT_DIR / "data" / "validation" / "sentence_families_diagnostic.json"


def load_json(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_provenance_graph() -> Tuple[int, int, List[str]]:
    errors = []
    
    # Load all graph nodes
    sources = {s["source_id"] for s in load_json(SOURCES_PATH).get("sources", [])}
    evidence = {e["evidence_id"]: e for e in load_json(EVIDENCE_PATH).get("evidence_items", [])}
    claims = {c["claim_id"]: c for c in load_json(CLAIMS_PATH).get("claims", [])}
    rules = {r["rule_id"]: r for r in load_json(RULES_PATH).get("rules", [])}
    constructions = {c["construction_id"]: c for c in load_json(CONSTRUCTIONS_PATH).get("constructions", [])}
    frames = {f["frame_id"]: f for f in load_json(FRAMES_PATH).get("frames", [])}
    families = load_json(FAMILIES_PATH).get("sentence_families", [])

    # 1. Check Evidence -> Source
    for eid, ev in evidence.items():
        sid = ev.get("source_id")
        if sid not in sources:
            errors.append(f"Evidence {eid} references unknown source_id '{sid}'")

    # 2. Check Claim -> Evidence
    for cid, clm in claims.items():
        for eid in clm.get("evidence_ids", []):
            if eid not in evidence:
                errors.append(f"Claim {cid} references unknown evidence_id '{eid}'")

    # 3. Check Rule -> Claim
    for rid, rul in rules.items():
        for cid in rul.get("supporting_claim_ids", []):
            if cid not in claims:
                errors.append(f"Rule {rid} references unknown claim_id '{cid}'")

    # 4. Check Construction -> Claim
    for const_id, const in constructions.items():
        for cid in const.get("supporting_claim_ids", []):
            if cid not in claims:
                errors.append(f"Construction {const_id} references unknown claim_id '{cid}'")

    # 5. Check Frame -> Construction
    for fid, frm in frames.items():
        for const_id in frm.get("compatible_constructions", []):
            if const_id not in constructions:
                errors.append(f"Frame {fid} references unknown construction_id '{const_id}'")

    # 6. Check SentenceFamily -> Frame & Construction
    for sf in families:
        sf_id = sf.get("sentence_family_id")
        fid = sf.get("semantic_frame_id")
        if fid not in frames:
            errors.append(f"Sentence family {sf_id} references unknown frame_id '{fid}'")
        
        cid = sf.get("primary_construction_id")
        if cid not in constructions:
            errors.append(f"Sentence family {sf_id} references unknown construction_id '{cid}'")

    total_chains = len(families)
    return total_chains, len(errors), errors


def main():
    print("==================================================")
    print("BLF Provenance Graph Integrity Validator")
    print("==================================================")

    total, err_count, errors = validate_provenance_graph()

    if errors:
        print(f"FAILED: {err_count} broken provenance link(s) found across {total} sentence family chains:")
        for err in errors:
            print(f"  - [FAIL] {err}")
        sys.exit(1)
    else:
        print(f"SUCCESS: Complete provenance graph verified across {total} sentence families (0 broken links).")
        sys.exit(0)


if __name__ == "__main__":
    main()
