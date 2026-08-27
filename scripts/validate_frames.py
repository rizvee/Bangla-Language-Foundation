#!/usr/bin/env python3
"""
BLF Semantic Frames Validator.

Validates:
1. Core frames catalog against schemas/v0_1/semantic_frame.schema.json.
2. Referential integrity to syntactic constructions (CONST-*).
3. Referential integrity of frame relations (target_frame_id).

Usage:
    python scripts/validate_frames.py
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

FRAME_SCHEMA_PATH = ROOT_DIR / "schemas" / "v0_1" / "semantic_frame.schema.json"
FRAMES_PATH = ROOT_DIR / "ontology" / "frames" / "core_frames.json"
CONSTRUCTIONS_PATH = ROOT_DIR / "ontology" / "constructions" / "constructions.json"


def load_json(path: Path) -> Dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_frames() -> Tuple[int, int, List[str]]:
    errors = []
    total_frames = 0

    schema = load_schema(FRAME_SCHEMA_PATH)
    frames_data = load_json(FRAMES_PATH)
    const_data = load_json(CONSTRUCTIONS_PATH)

    valid_const_ids = {c["construction_id"] for c in const_data.get("constructions", [])}
    frames = frames_data.get("frames", [])
    valid_frame_ids = {f["frame_id"] for f in frames}

    for f in frames:
        total_frames += 1
        fid = f.get("frame_id", "UNKNOWN")

        valid, schema_errs = validate_dict_against_schema(f, schema)
        if not valid:
            errors.append(f"Frame schema violation in {fid}: {schema_errs}")

        for const_id in f.get("compatible_constructions", []):
            if const_id not in valid_const_ids:
                errors.append(f"Frame {fid} references unknown construction '{const_id}'")

        for rel in f.get("frame_relations", []):
            target = rel.get("target_frame_id")
            if target and target not in valid_frame_ids:
                errors.append(f"Frame {fid} references unknown target frame relation '{target}'")

    return total_frames, len(errors), errors


def main():
    print("==================================================")
    print("BLF Semantic Frames Validator")
    print("==================================================")

    total, err_count, errors = validate_frames()

    if errors:
        print(f"FAILED: {err_count} violation(s) found across {total} semantic frames:")
        for err in errors:
            print(f"  - [FAIL] {err}")
        sys.exit(1)
    else:
        print(f"SUCCESS: All {total} semantic frames are VALID.")
        sys.exit(0)


if __name__ == "__main__":
    main()
