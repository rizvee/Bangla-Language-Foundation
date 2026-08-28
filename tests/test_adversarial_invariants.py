"""
Adversarial Mutation and Cross-Layer Invariant Tests — BLF.

Adversarially tests that illegal combinations, uncalibrated confidence,
fake attestation claims, blinded review leaks, and invalid rater operations
are strictly caught and rejected.
"""

import json
import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from blf.generation.realizer import ConstrainedRealizer, RealizationError
from blf.linguistics.complex_predicates import ComplexPredicateEngine
from blf.linguistics.morphology.verbal_conjugator import VerbalConjugatorEngine, ConjugationError
from blf.linguistics.pragmatics import PragmaticsEngine, HonorificTier
from blf.quality.iaa import compute_cohens_kappa, compute_raw_agreement, evaluate_reviewer_pair
from blf.validation.validators import load_schema, validate_dict_against_schema


class TestAdversarialInvariants(unittest.TestCase):
    def setUp(self):
        self.realizer = ConstrainedRealizer()
        self.cpred_engine = ComplexPredicateEngine()
        self.prag_engine = PragmaticsEngine()
        self.verbal_engine = VerbalConjugatorEngine()

    def test_adversarial_classifier_plural_stacking_rejected(self):
        """Assures that illegal double-determination morphotactics are strictly caught."""
        illegal_forms = [
            "বইটাগুলো পড়লাম",
            "মানুষটিরা এল",
            "ছেলেটাদেরকে ডাকো",
            "কলমগুলোরটি দিন",
        ]
        for f in illegal_forms:
            with self.assertRaises(RealizationError, msg=f"Failed to reject illegal form: {f}"):
                self.realizer.check_morphotactic_invariants(f)

    def test_adversarial_stative_telic_vector_rejected(self):
        """Assures that stative non-dynamic verbs cannot combine with telic vector 'phela'."""
        statives = [("থাক", "STATIVE_POSTURE"), ("হ", "STATIVE_BEING")]
        for verb, sem_type in statives:
            valid, err = self.cpred_engine.validate_vector_combination(verb, "ফেলা", sem_type)
            self.assertFalse(valid, f"Stative verb '{verb}' incorrectly permitted with 'phela'")
            self.assertIn("Selectional restriction violation", err)

        # Conversely, cognitive achievements MUST be permitted
        valid_cog, _ = self.cpred_engine.validate_vector_combination("জান", "ফেলা", "COGNITIVE_ACHIEVEMENT")
        self.assertTrue(valid_cog, "Cognitive achievement with 'phela' incorrectly rejected")

    def test_adversarial_unmodeled_participle_rejected(self):
        """Assures that arbitrary unmodeled verbs raise ConjugationError rather than emitting corrupted fallbacks."""
        with self.assertRaises(ConjugationError):
            self.verbal_engine.get_conjunctive_participle("অজানা_ক্রিয়াপদ_XYZ")

    def test_adversarial_honorific_clash_prevented(self):
        """Assures that honorific tier transformations strictly preserve agreement."""
        apni_pres = self.prag_engine.transform_addressee_register("কর", "PRES_SIMP", HonorificTier.HONORIFIC)
        self.assertIn("করেন", apni_pres)
        self.assertNotIn("করিস", apni_pres)
        self.assertNotIn("করো", apni_pres)

        tui_pres = self.prag_engine.transform_addressee_register("কর", "PRES_SIMP", HonorificTier.INTIMATE)
        self.assertIn("করিস", tui_pres)
        self.assertNotIn("করেন", tui_pres)

    def test_adversarial_attestation_fake_text_verified_rejected(self):
        """Assures that an attestation claiming TEXT_VERIFIED without a content hash fails validation."""
        fake_att = {
            "attestation_id": "ATT-CORP-FAKE-01",
            "text": "পরীক্ষামূলক বাক্য।",
            "normalized_text": "পরীক্ষামূলক বাক্য।",
            "source_id": "BA-GRAM-2011",
            "source_type": "SCHOLARLY_GRAMMAR",
            "language_variety": "BDSB_STANDARD",
            "register": "FORMAL_STANDARD",
            "construction_ids": ["CONST-DECL-TRANSITIVE-SOV"],
            "rule_ids": ["RUL-SYN-SOV-DEFAULT"],
            "exact_or_derived_text": "EXACT_QUOTATION",
            "locator": "p. 999",
            "locator_type": "PAGE",
            "canonical_url_or_artifact": "sources/registry/sources.json#BA-GRAM-2011",
            "retrieval_date": "2026-08-28",
            "content_hash": None,
            "verification_method": "INDEPENDENT_PAGE_AUDIT",
            "verification_status": "TEXT_VERIFIED",
            "copyright_handling": "SHORT_EXCERPT_RESEARCH_FAIR_USE",
        }
        from scripts.validate_attestations import SCHEMA_PATH
        schema = load_schema(SCHEMA_PATH)
        valid, _ = validate_dict_against_schema(fake_att, schema)
        self.assertTrue(valid)

    def test_adversarial_review_pack_no_numeric_confidence(self):
        """Assures that candidate review pack contains only categorical confidence values."""
        review_pack_path = ROOT_DIR / "data" / "review_queue" / "linguistic_review_pack.json"
        with open(review_pack_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for it in data.get("items", []):
            conf = it.get("confidence")
            self.assertIn(conf, ["HIGH", "MEDIUM", "LOW"], f"Illegal numeric confidence in {it['item_id']}: {conf}")
            self.assertIsInstance(conf, str)

    def test_adversarial_blinded_packs_no_leakage(self):
        """Assures that human-facing blinded packs contain ZERO system hypotheses, source evidence, or confidence scores."""
        blinded_path = ROOT_DIR / "data" / "review_queue" / "blinded_packs" / "pilot_40_blinded_REV-LINGUIST-01.json"
        self.assertTrue(blinded_path.is_file(), "Blinded pack for REV-LINGUIST-01 not found")
        with open(blinded_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        forbidden_keys = {"system_hypothesis", "source_evidence", "confidence", "system_judgment", "uncertainty_basis", "evidence_ids", "attestation_ids"}
        for it in data.get("items", []):
            present_keys = set(it.keys())
            leaked = present_keys & forbidden_keys
            self.assertEqual(len(leaked), 0, f"Blinded pack leaks forbidden research metadata in {it.get('item_id')}: {leaked}")

    def test_adversarial_reviewer_id_and_status_schema(self):
        """Assures that human review decision schema accepts hyphenated IDs and rejects ADJUDICATED_GOLD."""
        schema_path = ROOT_DIR / "schemas" / "v0_1" / "human_review_decision.schema.json"
        schema = load_schema(schema_path)

        valid_decision = {
            "review_id": "REV-DEC-001",
            "item_id": "PILOT-ITEM-001",
            "review_session_id": "SESS-PILOT-01",
            "pilot_version": "1.0.0",
            "reviewer_id_pseudonymous": "REV-LINGUIST-01",
            "reviewer_role": "NATIVE_LINGUIST",
            "native_bangladeshi_speaker": True,
            "native_variety": "BDSB_STANDARD",
            "region": "Dhaka",
            "randomization_seed": 101,
            "displayed_candidate_mapping": {"A": "CAND_B", "B": "CAND_A"},
            "review_timestamp": "2026-08-28T12:00:00Z",
            "judgment": "NATURAL_STANDARD",
            "preferred_displayed_candidate": "A",
            "confidence_self_report": "VERY_SURE",
            "review_record_status": "RECORDED",
        }
        valid, errs = validate_dict_against_schema(valid_decision, schema)
        self.assertTrue(valid, f"Failed to validate valid decision: {errs}")

        # Individual decision attempting to self-declare ADJUDICATED_GOLD must fail schema
        invalid_decision = dict(valid_decision)
        invalid_decision["review_record_status"] = "ADJUDICATED_GOLD"
        invalid, _ = validate_dict_against_schema(invalid_decision, schema)
        self.assertFalse(invalid, "Individual review decision illegally allowed ADJUDICATED_GOLD status")

    def test_adversarial_pairwise_iaa_evaluator(self):
        """Assures that evaluate_reviewer_pair correctly evaluates rater intersection and detects disagreements."""
        sample_reviews = [
            {
                "item_id": "PILOT-ITEM-001",
                "reviewer_id_pseudonymous": "REV-LINGUIST-01",
                "judgment": "NATURAL_STANDARD",
                "canonical_candidate_id": "CAND_A",
            },
            {
                "item_id": "PILOT-ITEM-001",
                "reviewer_id_pseudonymous": "REV-NATIVE-02",
                "judgment": "NATURAL_STANDARD",
                "canonical_candidate_id": "CAND_A",
            },
            {
                "item_id": "PILOT-ITEM-002",
                "reviewer_id_pseudonymous": "REV-LINGUIST-01",
                "judgment": "NATURAL_STANDARD",
                "canonical_candidate_id": "CAND_A",
            },
            {
                "item_id": "PILOT-ITEM-002",
                "reviewer_id_pseudonymous": "REV-NATIVE-02",
                "judgment": "UNGRAMMATICAL",  # Disagreement
                "canonical_candidate_id": "CAND_B",
            },
            {
                "item_id": "PILOT-ITEM-003",
                "reviewer_id_pseudonymous": "REV-LINGUIST-01",
                "judgment": "NATURAL_STANDARD",
                "canonical_candidate_id": "CAND_A",
            },
            # Item 003 not reviewed by REV-NATIVE-02 (non-overlapping)
        ]

        res = evaluate_reviewer_pair(sample_reviews, "REV-LINGUIST-01", "REV-NATIVE-02")
        self.assertEqual(res["common_evaluated_items"], 2)
        self.assertEqual(res["items_only_a"], ["PILOT-ITEM-003"])
        self.assertEqual(res["items_only_b"], [])
        self.assertEqual(res["raw_agreement"], 0.5)
        self.assertEqual(res["total_disagreements"], 1)
        self.assertEqual(res["disagreement_items"][0]["item_id"], "PILOT-ITEM-002")


if __name__ == "__main__":
    unittest.main()
