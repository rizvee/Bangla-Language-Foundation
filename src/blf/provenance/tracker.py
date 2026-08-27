"""
Provenance Tracking and Checksum Validation Utilities.
"""

import hashlib
import json
from pathlib import Path
from typing import Dict, Any, Optional


def compute_file_sha256(filepath: Path) -> str:
    """Computes the SHA-256 hash of a file."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    return sha256.hexdigest()


def compute_prompt_hash(prompt_text: str, parameters: Optional[Dict[str, Any]] = None) -> str:
    """Generates a deterministic hash for a prompt and its parameters."""
    canonical_payload = {
        "prompt": prompt_text.strip(),
        "parameters": parameters or {}
    }
    encoded = json.dumps(canonical_payload, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
