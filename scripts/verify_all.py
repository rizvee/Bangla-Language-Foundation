#!/usr/bin/env python3
"""
BLF Comprehensive Local Verification Suite.

Executes all automated test batteries, schema validators, source audits,
documentation consistency checks, and anti-AI-slop scanners.

Usage:
    python scripts/verify_all.py
"""

import subprocess
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT_DIR = Path(__file__).resolve().parent.parent


def run_stage(title: str, command: list) -> bool:
    print(f"\n{'=' * 60}")
    print(f"STAGE: {title}")
    print(f"COMMAND: {' '.join(command)}")
    print(f"{'=' * 60}")

    result = subprocess.run(command, cwd=ROOT_DIR)
    if result.returncode == 0:
        print(f"[PASS] {title} succeeded.")
        return True
    else:
        print(f"[FAIL] {title} failed with exit code {result.returncode}.")
        return False


def main() -> None:
    print("==================================================")
    print("BLF Complete Pre-Human Verification Suite")
    print("==================================================")

    stages = [
        ("Automated Unit Tests", [sys.executable, "-m", "unittest", "discover", "tests"]),
        ("10-Suite Schema & Knowledge Validators", [sys.executable, "scripts/validate_all.py"]),
        ("Documentation Consistency Checker", [sys.executable, "scripts/check_docs_consistency.py"]),
        ("Anti-AI-Slop & Writing Integrity Scanner", [sys.executable, "scripts/check_anti_slop.py"]),
    ]

    failed_stages = []
    for title, cmd in stages:
        success = run_stage(title, cmd)
        if not success:
            failed_stages.append(title)

    print("\n" + "=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)

    if failed_stages:
        print(f"FAILURE: {len(failed_stages)} stage(s) failed:")
        for stg in failed_stages:
            print(f"  - {stg}")
        sys.exit(1)
    else:
        print("SUCCESS: 100% of verification stages passed.")
        print("All research invariants, derivation chains, and test suites are intact.")
        sys.exit(0)


if __name__ == "__main__":
    main()
