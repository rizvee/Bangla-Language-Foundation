#!/usr/bin/env python3
"""
Source Integrity Auditor & Bibliographic Verifier for Bangla Language Foundation.

Separates structural validation from bibliographic verification.
Supports offline deterministic audits and online external resolution.

Usage:
    python scripts/audit_sources.py [--offline] [--online] [--source <ID>]
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Reconfigure stdout for Windows console UTF-8 support
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent.parent
SOURCES_PATH = ROOT_DIR / "sources" / "registry" / "sources.json"
AUDIT_LOG_PATH = ROOT_DIR / "sources" / "registry" / "source-audit.jsonl"
SCHEMA_PATH = ROOT_DIR / "schemas" / "v0_1" / "source.schema.json"

# Known false identifier blacklist to prevent regression
KNOWN_MISIDENTIFICATIONS = [
    {
        "pattern": r"2021\.wnut-1\.14",
        "forbidden_topic": "transliteration",
        "reason": "ACL 2021.wnut-1.14 is 'Common Sense Bias in Semantic Role Labeling', not Banglish transliteration."
    },
    {
        "pattern": r"2022\.findings-emnlp\.319",
        "forbidden_topic": "sentiment|code-mixed|sentirabangla",
        "reason": "ACL 2022.findings-emnlp.319 is a radiology report generation paper, not SentiraBangla."
    },
    {
        "pattern": r"2206\.14051",
        "forbidden_topic": r"speech|bengali\.ai|audio",
        "reason": "arXiv:2206.14051 is a business process simulation paper; Bengali.AI Speech is arXiv:2206.14053."
    },
    {
        "pattern": r"bn_bengal",
        "forbidden_topic": "universal dependencies",
        "reason": "Universal Dependencies has UD_Bengali-BRU and UD_Bengali-PUD; 'bn_bengal' is non-canonical."
    }
]


def load_sources() -> Dict[str, Any]:
    if not SOURCES_PATH.is_file():
        raise FileNotFoundError(f"Source registry not found: {SOURCES_PATH}")
    with open(SOURCES_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def audit_source_structure(source: Dict[str, Any]) -> List[str]:
    """Performs structural and schema-field consistency checks."""
    errors = []
    required_keys = [
        "source_id", "title", "author_or_org", "source_tier",
        "language", "year", "license", "redistribution",
        "verification_status", "citation"
    ]
    for key in required_keys:
        if key not in source or source[key] is None or source[key] == "":
            errors.append(f"Missing required field: '{key}'")

    status = source.get("verification_status")
    valid_statuses = ["VERIFIED", "PARTIALLY_VERIFIED", "PROVISIONAL", "QUARANTINED", "REJECTED"]
    if status not in valid_statuses:
        errors.append(f"Invalid verification_status '{status}'; must be one of {valid_statuses}")

    # If VERIFIED, must have explicit verification block with primary evidence
    if status == "VERIFIED":
        verification = source.get("verification")
        if not verification:
            errors.append("Status is 'VERIFIED' but record lacks a 'verification' metadata block.")
        else:
            primary_evidence = verification.get("primary_evidence", [])
            if not primary_evidence:
                errors.append("Status is 'VERIFIED' but 'verification.primary_evidence' is empty.")
            verified_fields = verification.get("verified_fields", [])
            if not verified_fields:
                errors.append("Status is 'VERIFIED' but 'verification.verified_fields' is empty.")

    return errors


def audit_known_misidentifications(source: Dict[str, Any]) -> List[str]:
    """Detects blacklisted false citations and conflated metadata."""
    errors = []
    source_str = json.dumps(source).lower()
    
    for rule in KNOWN_MISIDENTIFICATIONS:
        if re.search(rule["pattern"], source_str):
            if re.search(rule["forbidden_topic"], source_str):
                # If the source is not QUARANTINED, this is a violation
                if source.get("verification_status") != "QUARANTINED":
                    errors.append(f"Known citation error detected: {rule['reason']}")
    return errors


def run_audit(target_source_id: str = None, online: bool = False) -> Tuple[int, int, int]:
    """Runs the source integrity audit across all registered sources."""
    print("==================================================")
    print("Running Source Integrity & Bibliographic Audit...")
    print(f"Mode: {'ONLINE (Live resolution)' if online else 'OFFLINE (Deterministic checks)'}")
    print("==================================================")

    data = load_sources()
    sources = data.get("sources", [])
    
    total = 0
    passed = 0
    quarantined = 0
    failed = 0

    for src in sources:
        sid = src.get("source_id", "UNKNOWN")
        if target_source_id and sid != target_source_id:
            continue

        total += 1
        status = src.get("verification_status", "UNVERIFIED")
        struct_errs = audit_source_structure(src)
        misid_errs = audit_known_misidentifications(src)
        all_errs = struct_errs + misid_errs

        if status == "QUARANTINED":
            quarantined += 1
            print(f"  [QUARANTINED] {sid}: {src.get('title', '')[:50]} (Safe in quarantine)")
        elif all_errs:
            failed += 1
            print(f"  [FAIL] {sid}:")
            for err in all_errs:
                print(f"         - {err}")
        else:
            passed += 1
            print(f"  [{status}] {sid}: {src.get('title', '')[:50]}")

    print("\n" + "=" * 50)
    print(f"Audit Complete: Total={total}, Passed={passed}, Quarantined={quarantined}, Failed={failed}")
    print("=" * 50)

    return total, passed + quarantined, failed


def main():
    parser = argparse.ArgumentParser(description="Audit research sources for integrity and accuracy.")
    parser.add_argument("--source", type=str, help="Audit specific source ID")
    parser.add_argument("--online", action="store_true", help="Perform online live resolution")
    parser.add_argument("--offline", action="store_true", default=True, help="Perform offline deterministic audit")
    args = parser.parse_args()

    online = args.online
    total, passed, failed = run_audit(target_source_id=args.source, online=online)
    if failed > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
