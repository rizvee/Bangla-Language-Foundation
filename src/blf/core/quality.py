"""
Quality Tier Auditing and Validation Logic.
"""

from typing import Dict, Any, Tuple, List
from blf.linguistics.tags import QualityTier


def validate_tier_invariants(record: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validates quality tier constraints on an utterance record.
    - If SYNTHETIC, synthetic_provenance must be present.
    - If GOLD, validation_status must be 'passed' and quality_score must be >= 0.9.
    """
    errors = []
    tier = record.get("quality_tier")

    if tier not in [t.value for t in QualityTier]:
        errors.append(f"Invalid quality_tier: {tier}")
        return False, errors

    if tier == QualityTier.SYNTHETIC.value:
        if "synthetic_provenance" not in record or not record["synthetic_provenance"]:
            errors.append("SYNTHETIC records must have a non-empty 'synthetic_provenance' block.")

    if tier == QualityTier.GOLD.value:
        status = record.get("validation_status")
        if status != "passed":
            errors.append(f"GOLD records must have validation_status='passed', got '{status}'.")
        score = record.get("quality_score", 0.0)
        if score < 0.9:
            errors.append(f"GOLD records must have quality_score >= 0.9, got {score}.")

    return len(errors) == 0, errors
