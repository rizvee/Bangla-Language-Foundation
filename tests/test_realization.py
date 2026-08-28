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


    def test_feature_sensitive_dom_realization(self):
        from blf.linguistics.dom import ObjectFeatures, AnimacyTier, DefinitenessTier, SpecificityTier

        # 1. Non-specific human -> Bare direct object (Ami daktar khujchi)
        feat_doc = ObjectFeatures(
            lemma="ডাক্তার",
            animacy=AnimacyTier.HUMAN,
            definiteness=DefinitenessTier.BARE_GENERIC,
            specificity=SpecificityTier.NON_SPECIFIC,
        )
        res_doc = self.realizer.realize_transitive(
            "আমরা", "ডাক্তার", "খুঁজ", tense_key="PRES_CONT", person_slot="1", object_features=feat_doc
        )
        self.assertEqual(res_doc, "আমরা ডাক্তার খুঁজছি।")

        # 2. Specific human with classifier -> -ke (Chhatro-ti-ke daklam)
        feat_student = ObjectFeatures(
            lemma="ছাত্র",
            animacy=AnimacyTier.HUMAN,
            definiteness=DefinitenessTier.DEFINITE,
            specificity=SpecificityTier.SPECIFIC,
            has_classifier=True,
            classifier="টি",
        )
        res_student = self.realizer.realize_transitive(
            "শিক্ষক", "ছাত্র", "ডাক", tense_key="PAST_SIMP", person_slot="3_HON", object_features=feat_student
        )
        self.assertEqual(res_student, "শিক্ষক ছাত্রটিকে ডাকলেন।")

    def test_polarity_and_question_realization(self):
        # 1. Present Perfect + NEG -> -ni
        res_neg = self.realizer.realize_transitive(
            "আমি", "কাজটা", "কর", tense_key="PRES_PERF", person_slot="1", polarity="NEGATIVE"
        )
        self.assertEqual(res_neg, "আমি কাজটা করিনি।")

        # 2. Polar Question Topic-Adjacent Placement
        res_pq_topic = self.realizer.realize_transitive(
            "তুমি", "ঢাকা", "যা", tense_key="FUT_SIMP", person_slot="2_ORD",
            is_polar_question=True, polar_question_position="topic_adjacent"
        )
        self.assertEqual(res_pq_topic, "তুমি কি ঢাকা যাবে ?")

        # 3. Polar Question Sentence-Final Placement
        res_pq_final = self.realizer.realize_transitive(
            "তুমি", "ঢাকা", "যা", tense_key="FUT_SIMP", person_slot="2_ORD",
            is_polar_question=True, polar_question_position="sentence_final"
        )
        self.assertEqual(res_pq_final, "তুমি ঢাকা যাবে কি ?")

    def test_inanimate_demonstrative_and_contrast_dom(self):
        from blf.linguistics.dom import DOMEngine, ObjectFeatures, AnimacyTier, DefinitenessTier, SpecificityTier, FocusProminence
        dom = DOMEngine()

        # Demonstrative inanimate under contrastive focus -> licenses overt -ke as accepted variant
        feat_dem = ObjectFeatures(
            lemma="এটা",
            animacy=AnimacyTier.INANIMATE,
            definiteness=DefinitenessTier.DEFINITE,
            specificity=SpecificityTier.SPECIFIC,
            is_demonstrative=True,
            prominence=FocusProminence.CONTRASTIVE,
        )
        dec = dom.evaluate_dom(feat_dem)
        self.assertEqual(dec.status, "ATTESTED_CONTEXT_DEPENDENT")
        self.assertEqual(dec.accepted_variant, "এটাকে")
        self.assertIsNotNone(dec.source_conflict)
        self.assertEqual(dec.confidence, "MEDIUM")

    def test_cognitive_achievement_vector_sentence(self):
        res_cog = self.realizer.realize_vector_predicate_sentence(
            "সে", "সত্যটা", "জান", "ফেলা", "COGNITIVE_ACHIEVEMENT", "PAST_SIMP.3_ORD"
        )
        self.assertEqual(res_cog, "সে সত্যটা জেনে ফেলল।")


if __name__ == "__main__":
    unittest.main()
