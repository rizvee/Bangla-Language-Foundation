"""
Unit tests for JSON Schemas and Fixture Validation.
"""

import unittest
import json
from pathlib import Path
import sys

# Ensure src is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from blf.validation.validators import load_schema, validate_dict_against_schema
from blf.core.quality import validate_tier_invariants


class TestSchemas(unittest.TestCase):
    def setUp(self):
        self.root_dir = Path(__file__).parent.parent
        self.schemas_dir = self.root_dir / "schemas" / "v0_1"
        self.fixtures_dir = self.root_dir / "data" / "validation" / "fixtures"

        self.utterance_schema = load_schema(self.schemas_dir / "utterance.schema.json")
        self.sentence_family_schema = load_schema(self.schemas_dir / "sentence_family.schema.json")
        self.source_schema = load_schema(self.schemas_dir / "source.schema.json")
        self.provenance_schema = load_schema(self.schemas_dir / "synthetic_provenance.schema.json")

    def test_gold_fixture_validation(self):
        with open(self.fixtures_dir / "fixture_gold_utterance.json", "r", encoding="utf-8") as f:
            gold_data = json.load(f)

        valid, errors = validate_dict_against_schema(gold_data, self.utterance_schema)
        self.assertTrue(valid, f"Gold fixture validation failed: {errors}")

        tier_valid, tier_errors = validate_tier_invariants(gold_data)
        self.assertTrue(tier_valid, f"Gold tier invariant failed: {tier_errors}")

    def test_synthetic_fixture_validation(self):
        with open(self.fixtures_dir / "fixture_synthetic_utterance.json", "r", encoding="utf-8") as f:
            synth_data = json.load(f)

        valid, errors = validate_dict_against_schema(synth_data, self.utterance_schema)
        self.assertTrue(valid, f"Synthetic fixture validation failed: {errors}")

        tier_valid, tier_errors = validate_tier_invariants(synth_data)
        self.assertTrue(tier_valid, f"Synthetic tier invariant failed: {tier_errors}")

    def test_missing_required_field_fails(self):
        incomplete_data = {
            "utterance_id": "UTT-99999",
            "raw_text": "টেস্ট বাক্য"
        }
        valid, errors = validate_dict_against_schema(incomplete_data, self.utterance_schema)
        self.assertFalse(valid)
        self.assertTrue(any("sentence_family_id" in err for err in errors))

    def test_invalid_register_fails(self):
        invalid_data = {
            "utterance_id": "UTT-99999",
            "sentence_family_id": "SF-00001",
            "raw_text": "টেস্ট বাক্য",
            "normalized_text": "টেস্ট বাক্য",
            "canonical_bangla": "টেস্ট বাক্য",
            "english_translation": "Test sentence",
            "register": "INVALID_REGISTER_XYZ",
            "dialect": "bdsb_standard",
            "code_switching_type": "pure_bangla",
            "quality_tier": "SILVER",
            "validation_status": "passed"
        }
        valid, errors = validate_dict_against_schema(invalid_data, self.utterance_schema)
        self.assertFalse(valid)
        self.assertTrue(any("register" in err for err in errors))

    def test_synthetic_without_provenance_fails(self):
        fake_synth = {
            "utterance_id": "UTT-99999",
            "sentence_family_id": "SF-00001",
            "raw_text": "টেস্ট বাক্য",
            "normalized_text": "টেস্ট বাক্য",
            "canonical_bangla": "টেস্ট বাক্য",
            "english_translation": "Test sentence",
            "register": "colloquial_standard",
            "dialect": "bdsb_standard",
            "code_switching_type": "pure_bangla",
            "quality_tier": "SYNTHETIC",
            "validation_status": "passed"
        }
        valid, errors = validate_tier_invariants(fake_synth)
        self.assertFalse(valid)
        self.assertTrue(any("synthetic_provenance" in err for err in errors))


if __name__ == "__main__":
    unittest.main()
