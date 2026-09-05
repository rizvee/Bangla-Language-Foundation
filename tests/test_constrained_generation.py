"""
Unit tests for Constrained Synthetic Generation Pipeline and Anti-Cartesian Restrictions.
"""

import json
from pathlib import Path
import unittest

from blf.generation.pipeline import ConstrainedGenerationPipeline, SelectionalRestrictionError
from blf.validation.validators import validate_dict_against_schema


class TestConstrainedGeneration(unittest.TestCase):

    def setUp(self) -> None:
        self.pipeline = ConstrainedGenerationPipeline()
        self.root_dir = Path(__file__).resolve().parent.parent
        schema_path = self.root_dir / "schemas" / "v0_1" / "synthetic_provenance.schema.json"
        with open(schema_path, "r", encoding="utf-8") as f:
            self.provenance_schema = json.load(f)

    def test_valid_synthetic_generation_and_schema_compliance(self) -> None:
        record = self.pipeline.generate_synthetic_record(
            frame_id="FRAME-INGESTION-FOOD",
            construction_id="CONST-DECL-TRANSITIVE-SOV",
            agent_lemma="সে",
            patient_lemma="ভাত",
            verb_root="খা",
            tense_key="PRES_SIMP",
            person_slot="3_ORD",
            polarity="AFFIRMATIVE",
        )

        # Invariant checks
        self.assertEqual(record["text"], "সে ভাত খায়।")
        self.assertEqual(record["execution_tag"], "SYNTHETIC_SOFTWARE_TEST_ONLY")
        self.assertEqual(record["quality_tier"], "SYNTHETIC")
        self.assertEqual(record["provenance_class"], "RULE_GENERATED")

        # Validate provenance block against official JSON schema
        valid, errors = validate_dict_against_schema(record["provenance"], self.provenance_schema)
        self.assertTrue(valid, f"Provenance validation errors: {errors}")

    def test_inanimate_agent_blocked_for_ingestion(self) -> None:
        with self.assertRaises(SelectionalRestrictionError):
            self.pipeline.generate_synthetic_record(
                frame_id="FRAME-INGESTION-FOOD",
                construction_id="CONST-DECL-TRANSITIVE-SOV",
                agent_lemma="গাড়ি",  # Inanimate agent
                patient_lemma="ভাত",
                verb_root="খা",
            )

    def test_non_edible_patient_blocked_for_food_ingestion(self) -> None:
        with self.assertRaises(SelectionalRestrictionError):
            self.pipeline.generate_synthetic_record(
                frame_id="FRAME-INGESTION-FOOD",
                construction_id="CONST-DECL-TRANSITIVE-SOV",
                agent_lemma="সে",
                patient_lemma="পাথর",  # Non-edible
                verb_root="খা",
            )

    def test_solid_patient_blocked_for_liquid_ingestion(self) -> None:
        with self.assertRaises(SelectionalRestrictionError):
            self.pipeline.generate_synthetic_record(
                frame_id="FRAME-INGESTION-LIQUID",
                construction_id="CONST-DECL-TRANSITIVE-SOV",
                agent_lemma="সে",
                patient_lemma="ভাত",  # Non-liquid
                verb_root="খা",
            )

    def test_zero_production_data_invariant(self) -> None:
        # Ensures that test generation operates in-memory and does not write to production data/corpus
        prod_corpus = self.root_dir / "data" / "corpus"
        if prod_corpus.exists():
            files = list(prod_corpus.glob("*.json")) + list(prod_corpus.glob("*.jsonl"))
            self.assertEqual(len(files), 0, "Zero production corpus records invariant violated!")


if __name__ == "__main__":
    unittest.main()
