"""
Unit tests for BLF Constrained Realizer and Diagnostic Sentence Families.
"""

import json
import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from blf.generation.realizer import ConstrainedRealizer, RealizationError
from blf.validation.validators import load_schema, validate_dict_against_schema

DIAGNOSTIC_PATH = ROOT_DIR / "data" / "validation" / "sentence_families_diagnostic.json"
SCHEMA_PATH = ROOT_DIR / "schemas" / "v0_1" / "sentence_family.schema.json"


class TestRealization(unittest.TestCase):
    def setUp(self):
        self.realizer = ConstrainedRealizer()
        self.schema = load_schema(SCHEMA_PATH)
        with open(DIAGNOSTIC_PATH, "r", encoding="utf-8") as f:
            self.diagnostic = json.load(f)

    def test_diagnostic_sentence_families_schema(self):
        for sf in self.diagnostic["sentence_families"]:
            sf_id = sf.get("sentence_family_id")
            valid, errors = validate_dict_against_schema(sf, self.schema)
            self.assertTrue(valid, f"Sentence family {sf_id} failed schema: {errors}")

    def test_transitive_sov_realization(self):
        # 1. Animate DOM: manush-ke dekhlam
        res_anim = self.realizer.realize_transitive(
            "আমি", "মানুষ", "দেখ", tense_key="PAST_SIMP", person_slot="1", is_animate_obj=True
        )
        self.assertEqual(res_anim, "আমি মানুষকে দেখলাম।")

        # 2. Inanimate unmarked direct object: boi porlam
        res_inanim = self.realizer.realize_transitive(
            "আমি", "বই", "পড়", tense_key="PAST_SIMP", person_slot="1", is_animate_obj=False
        )
        self.assertEqual(res_inanim, "আমি বই পড়লাম।")

    def test_topicalization_and_prodrop(self):
        # Topicalized OSV
        res_top = self.realizer.realize_transitive(
            "সে", "চিঠিটা", "লিখ", tense_key="PRES_SIMP", person_slot="3_ORD", is_topicalized=True
        )
        self.assertEqual(res_top, "চিঠিটা সে লেখে।")

        # Pro-drop OV
        res_pd = self.realizer.realize_transitive(
            "সে", "ভাত", "খা", tense_key="PRES_SIMP", person_slot="3_ORD", is_pro_drop=True
        )
        self.assertEqual(res_pd, "ভাত খায়।")

    def test_ditransitive_transfer_realization(self):
        res_ditr = self.realizer.realize_ditransitive("শিক্ষক", "ছাত্র", "কলমটা", "দে", "PAST_SIMP", "3_HON")
        self.assertEqual(res_ditr, "শিক্ষক ছাত্রকে কলমটা দিলেন।")

    def test_vector_predicate_sentence_realization(self):
        res_vec = self.realizer.realize_vector_predicate_sentence(
            "সে", "ভাত", "খা", "ফেলা", "TRANSITIVE_DYNAMIC", "PAST_SIMP.3_ORD"
        )
        self.assertEqual(res_vec, "সে ভাত খেয়ে ফেলল।")

    def test_invariant_rejections(self):
        # Reject illegal stacked affixes
        with self.assertRaises(RealizationError):
            self.realizer.check_morphotactic_invariants("বইটাগুলো পড়ে")

        # Reject invalid vector selection
        with self.assertRaises(RealizationError):
            self.realizer.realize_vector_predicate_sentence(
                "সে", "খবরটা", "জান", "ফেলা", "STATIVE_COGNITION"
            )


if __name__ == "__main__":
    unittest.main()
