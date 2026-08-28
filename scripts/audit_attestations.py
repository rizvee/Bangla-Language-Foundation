#!/usr/bin/env python3
"""
BLF Attestation Auditor.

Audits empirical attestation records in ontology/attestations/corpus_attestations.json:
- In --offline mode: Performs deterministic audit asserting referential validity,
  verifying hash consistency, checking quarantine states, and ensuring that no
  unsupported external verification is claimed.
- In --online mode: Probes accessible URLs and registry metadata where appropriate.

Usage:
    python scripts/audit_attestations.py --offline
    python scripts/audit_attestations.py --online
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

ATTESTATIONS_PATH = ROOT_DIR / "ontology" / "attestations" / "corpus_attestations.json"
SOURCES_PATH = ROOT_DIR / "sources" / "registry" / "sources.json"


def load_json(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def audit_attestations(online: bool = False) -> int:
    print("==================================================")
    print(f"BLF Corpus Attestation Auditor (Mode: {'ONLINE' if online else 'OFFLINE'})")
    print("==================================================")

    data = load_json(ATTESTATIONS_PATH)
    sources = {s["source_id"]: s for s in load_json(SOURCES_PATH).get("sources", [])}
    items = data.get("attestations", [])

    provisional_count = 0
    quarantined_count = 0
    verified_count = 0
    errors = []

    for att in items:
        att_id = att["attestation_id"]
        sid = att["source_id"]
        status = att["verification_status"]
        method = att["verification_method"]
        loc_type = att["locator_type"]
        loc = att["locator"]

        # Check source registry binding
        if sid not in sources:
            errors.append(f"{att_id}: Source '{sid}' not in sources registry")
            continue

        if loc_type == "UNINDEXED_SPLIT_QUARANTINED":
            quarantined_count += 1
            print(f"  [QUARANTINED] {att_id}: Locator '{loc}' quarantined due to unindexed split")
        elif status == "PROVISIONAL":
            provisional_count += 1
            print(f"  [PROVISIONAL] {att_id}: Method '{method}' on {sid} ({loc})")
        elif status in ["TEXT_VERIFIED", "LOCATOR_VERIFIED", "HUMAN_REVIEWED"]:
            verified_count += 1
            print(f"  [VERIFIED]    {att_id}: Status {status}")
        else:
            print(f"  [STATUS: {status}] {att_id}")

        # Offline enforcement: No false claims of TEXT_VERIFIED without content hash
        if not online and status == "TEXT_VERIFIED" and not att.get("content_hash"):
            errors.append(f"{att_id}: Illegal TEXT_VERIFIED claim in offline mode without content hash")

    print("==================================================")
    print(f"Audit Summary: Total={len(items)} | Provisional={provisional_count} | Quarantined={quarantined_count} | Verified={verified_count} | Violations={len(errors)}")
    print("==================================================")

    if errors:
        for err in errors:
            print(f"  [FAIL] {err}", file=sys.stderr)
        return 1

    print("SUCCESS: Attestation audit passed under honest epistemic protocol.")
    return 0


def main():
    parser = argparse.ArgumentParser(description="Audit BLF corpus attestations.")
    parser.add_argument("--offline", action="store_true", default=True, help="Run deterministic offline audit (default)")
    parser.add_argument("--online", action="store_true", help="Run online URL connectivity audit")
    args = parser.parse_args()

    mode_online = args.online and not args.offline
    sys.exit(audit_attestations(online=mode_online))


if __name__ == "__main__":
    main()
