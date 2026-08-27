#!/usr/bin/env python3
"""
BLF Unified Master Validator.

Executes all authoritative project verification suites:
1. Schema & test fixture validation (scripts/validate_schemas.py)
2. Primary source & license audit (scripts/audit_sources.py)
3. Linguistic knowledge layer validation (scripts/validate_knowledge.py)
4. Morphological paradigm validation (scripts/validate_paradigms.py)
5. Construction grammar & complex predicates validation (scripts/validate_constructions.py)
6. Semantic frames validation (scripts/validate_frames.py)
7. Sentence families & realization validation (scripts/validate_sentence_families.py)
8. Provenance graph integrity validation (scripts/validate_provenance_graph.py)
9. Anti-AI-slop & documentation consistency (scripts/check_anti_slop.py)

Usage:
    python scripts/validate_all.py
"""

import subprocess
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent.parent

VALIDATION_SCRIPTS = [
    ("Schema & Fixtures", ROOT_DIR / "scripts" / "validate_schemas.py"),
    ("Source Registry Audit", ROOT_DIR / "scripts" / "audit_sources.py"),
    ("Linguistic Knowledge", ROOT_DIR / "scripts" / "validate_knowledge.py"),
    ("Morphological Paradigms", ROOT_DIR / "scripts" / "validate_paradigms.py"),
    ("Constructions & Complex Predicates", ROOT_DIR / "scripts" / "validate_constructions.py"),
    ("Semantic Frames", ROOT_DIR / "scripts" / "validate_frames.py"),
    ("Sentence Families & Realization", ROOT_DIR / "scripts" / "validate_sentence_families.py"),
    ("Provenance Graph Integrity", ROOT_DIR / "scripts" / "validate_provenance_graph.py"),
    ("Anti-AI-Slop Scanner", ROOT_DIR / "scripts" / "check_anti_slop.py"),
]


def run_script(name: str, script_path: Path) -> bool:
    print(f"\n--- Running: {name} ({script_path.name}) ---")
    res = subprocess.run([sys.executable, str(script_path)], capture_output=True, text=True, encoding="utf-8")
    if res.stdout:
        print(res.stdout.strip())
    if res.returncode != 0:
        if res.stderr:
            print(res.stderr.strip(), file=sys.stderr)
        print(f"[FAIL] {name} failed with exit code {res.returncode}")
        return False
    print(f"[PASS] {name} passed.")
    return True


def main():
    print("==================================================")
    print("BLF Unified Master Validation Suite")
    print("==================================================")

    failed_suites = []
    for name, script_path in VALIDATION_SCRIPTS:
        if not script_path.is_file():
            print(f"[ERROR] Script not found: {script_path}")
            failed_suites.append(name)
            continue
        success = run_script(name, script_path)
        if not success:
            failed_suites.append(name)

    print("\n" + "=" * 50)
    if failed_suites:
        print(f"FAILED: {len(failed_suites)} validation suite(s) failed:")
        for fs in failed_suites:
            print(f"  - [FAIL] {fs}")
        sys.exit(1)
    else:
        print(f"SUCCESS: All {len(VALIDATION_SCRIPTS)} validation suites passed (100% verified).")
        sys.exit(0)


if __name__ == "__main__":
    main()
