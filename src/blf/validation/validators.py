"""
Validation Engine for Schemas, Records, and Provenance.
"""

import json
from pathlib import Path
from typing import Dict, Any, Tuple, List, Optional

try:
    import jsonschema
    HAS_JSONSCHEMA = True
except ImportError:
    HAS_JSONSCHEMA = False


def load_schema(schema_path: Path) -> Dict[str, Any]:
    """Loads a JSON Schema from a file."""
    with open(schema_path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_dict_against_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates a data dictionary against a JSON schema.
    Uses jsonschema library if available, otherwise performs basic schema checks.
    """
    errors: List[str] = []

    if HAS_JSONSCHEMA:
        try:
            resolver = jsonschema.RefResolver(
                base_uri=f"file:///{Path(__file__).parent.parent.parent.parent.resolve().as_posix()}/schemas/v0_1/",
                referrer=schema
            )
            validator = jsonschema.Draft7Validator(schema, resolver=resolver)
            for err in validator.iter_errors(data):
                errors.append(f"{err.json_path}: {err.message}")
            return len(errors) == 0, errors
        except Exception as e:
            # If RefResolver or draft fails, fallback to basic check
            pass

    # Built-in fallback validation
    req_fields = schema.get("required", [])
    for field in req_fields:
        if field not in data:
            errors.append(f"Missing required field: '{field}'")

    props = schema.get("properties", {})
    for key, val in data.items():
        if key in props:
            spec = props[key]
            expected_type = spec.get("type")
            if expected_type == "string" and not isinstance(val, str):
                errors.append(f"Field '{key}' expected string, got {type(val).__name__}")
            elif expected_type == "integer" and not isinstance(val, int):
                errors.append(f"Field '{key}' expected int, got {type(val).__name__}")
            elif expected_type == "number" and not isinstance(val, (int, float)):
                errors.append(f"Field '{key}' expected number, got {type(val).__name__}")
            elif expected_type == "array" and not isinstance(val, list):
                errors.append(f"Field '{key}' expected list, got {type(val).__name__}")
            elif expected_type == "object" and not isinstance(val, dict):
                errors.append(f"Field '{key}' expected dict, got {type(val).__name__}")

            if "enum" in spec and val not in spec["enum"]:
                errors.append(f"Field '{key}' value '{val}' not in allowed enum {spec['enum']}")

    return len(errors) == 0, errors
