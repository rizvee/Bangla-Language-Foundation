#!/usr/bin/env python3
"""
Validates the Research Source Registry (sources/registry/sources.json).
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
    registry_path = root_dir / "sources" / "registry" / "sources.json"
    schema_path = root_dir / "schemas" / "v0_1" / "source.schema.json"

    if not registry_path.exists():
        print(f"Registry not found: {registry_path}")
        sys.exit(1)

    if not schema_path.exists():
        print(f"Schema not found: {schema_path}")
        sys.exit(1)

    with open(registry_path, "r", encoding="utf-8") as f:
        registry = json.load(f)

    source_schema = load_schema(schema_path)
    sources = registry.get("sources", [])
    print(f"Validating {len(sources)} source entries in {registry_path.name}...")

    has_errors = False
    seen_ids = set()

    for entry in sources:
        sid = entry.get("source_id", "UNKNOWN")
        if sid in seen_ids:
            print(f"  [ERROR] Duplicate source_id: '{sid}'")
            has_errors = True
        seen_ids.add(sid)

        valid, errors = validate_dict_against_schema(entry, source_schema)
        if valid:
            print(f"  [OK] {sid} ({entry.get('source_tier', 'N/A')}): {entry.get('title', '')[:50]}")
        else:
            print(f"  [FAIL] {sid}: {errors}")
            has_errors = True

    print("\n" + "=" * 50)
    if has_errors:
        print("Source registry validation FAILED.")
        sys.exit(1)
    else:
        print(f"Source registry VALID: {len(sources)} entries verified.")
        sys.exit(0)


if __name__ == "__main__":
    main()
