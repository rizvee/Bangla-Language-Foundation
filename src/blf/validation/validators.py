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
    def _validate_node(val: Any, spec: Dict[str, Any], path: str) -> None:
        expected_type = spec.get("type")
        if expected_type == "string" and not isinstance(val, str):
            errors.append(f"{path}: expected string, got {type(val).__name__}")
        elif expected_type == "integer" and not isinstance(val, int):
            errors.append(f"{path}: expected int, got {type(val).__name__}")
        elif expected_type == "number" and not isinstance(val, (int, float)):
            errors.append(f"{path}: expected number, got {type(val).__name__}")
        elif expected_type == "boolean" and not isinstance(val, bool):
            errors.append(f"{path}: expected bool, got {type(val).__name__}")
        elif expected_type == "array" and not isinstance(val, list):
            errors.append(f"{path}: expected list, got {type(val).__name__}")
        elif expected_type == "object" and not isinstance(val, dict):
            errors.append(f"{path}: expected dict, got {type(val).__name__}")

        if "enum" in spec and val not in spec["enum"]:
            errors.append(f"{path}: value '{val}' not in allowed enum {spec['enum']}")

        if isinstance(val, list):
            if spec.get("uniqueItems") and len(val) != len(set(val)):
                errors.append(f"{path}: list contains duplicates: {val}")
            item_spec = spec.get("items")
            if isinstance(item_spec, dict):
                for idx, item in enumerate(val):
                    _validate_node(item, item_spec, f"{path}[{idx}]")

        elif isinstance(val, dict):
            reqs = spec.get("required", [])
            for r in reqs:
                if r not in val:
                    errors.append(f"{path}: Missing required field '{r}'")

            props = spec.get("properties", {})
            if spec.get("additionalProperties") is False:
                extra_keys = set(val.keys()) - set(props.keys())
                if extra_keys:
                    errors.append(f"{path}: unallowed additional properties: {extra_keys}")

            prop_names = spec.get("propertyNames", {})
            if "enum" in prop_names:
                for k in val.keys():
                    if k not in prop_names["enum"]:
                        errors.append(f"{path}: property key '{k}' not in allowed enum {prop_names['enum']}")

            for k, child_val in val.items():
                if k in props:
                    _validate_node(child_val, props[k], f"{path}.{k}")
                elif "additionalProperties" in spec and isinstance(spec["additionalProperties"], dict):
                    _validate_node(child_val, spec["additionalProperties"], f"{path}.{k}")

    _validate_node(data, schema, "$")
    return len(errors) == 0, errors
