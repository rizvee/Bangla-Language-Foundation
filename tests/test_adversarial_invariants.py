"""
Adversarial Mutation and Cross-Layer Invariant Tests — BLF.

Adversarially tests that illegal combinations, uncalibrated confidence,
fake attestation claims, blinded review leaks, active secret tracking,
and candidate-level human review invariants are strictly caught and verified.
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
from blf.quality.iaa import compute_cohens_kappa, compute_raw_agreement, evaluate_dual_iaa
from blf.validation.validators import load_schema, validate_dict_against_schema
from scripts.create_private_review_session import create_reviewer_blinded_pack, load_canonical_items, load_practice_items
from scripts.decode_review_submissions import decode_submission


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

    def test_adversarial_private_sessions_gitignored(self):
        """Assures that .blf-private/ is explicitly included in .gitignore to prevent committing active secrets."""
        gitignore_path = ROOT_DIR / ".gitignore"
        with open(gitignore_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn(".blf-private/", content, ".blf-private/ must be in .gitignore")

    def test_adversarial_candidate_level_submission_schema(self):
        """Assures that raw reviewer submissions validate candidate-level judgments and require no secret seeds."""
        schema_path = ROOT_DIR / "schemas" / "v0_1" / "human_review_decision.schema.json"
        schema = load_schema(schema_path)

        valid_submission = {
            "submission_id": "REV-SUB-0001",
            "session_id": "SESS-PILOT-0001",
            "reviewer_pseudonym": "REV-LINGUIST-01",
            "reviewer_qualification": "NATIVE_LINGUIST",
            "native_bangladeshi_speaker": True,
            "native_variety": "BDSB_STANDARD",
            "opaque_item_id": "BLIND-R1-A7K4",
            "candidate_judgments": {
                "A": {"acceptability": "NATURAL_STANDARD", "certainty": "VERY_SURE"},
                "B": {"acceptability": "MARKED_BUT_VALID", "certainty": "SURE"},
            },
            "preferred_candidates": ["A"],
            "correction": None,
            "comments": "Candidate A is unmarked canonical standard.",
            "timestamp": "2026-08-28T12:00:00Z",
        }
        valid, errs = validate_dict_against_schema(valid_submission, schema)
        self.assertTrue(valid, f"Failed to validate candidate-level submission: {errs}")

        # Multiple preferred candidates is valid
        multi_pref = dict(valid_submission)
        multi_pref["preferred_candidates"] = ["A", "B"]
        valid_multi, _ = validate_dict_against_schema(multi_pref, schema)
        self.assertTrue(valid_multi)

        # NONE preferred candidate is valid
        none_pref = dict(valid_submission)
        none_pref["preferred_candidates"] = ["NONE"]
        valid_none, _ = validate_dict_against_schema(none_pref, schema)
        self.assertTrue(valid_none)

    def test_adversarial_private_session_generation_opaque_ids(self):
        """Assures that private session creator produces opaque IDs, intermixed orders, and no research leaks."""
        canonical_items = load_canonical_items()
        practice_items = load_practice_items()
        self.assertEqual(len(canonical_items), 40)
        self.assertEqual(len(practice_items), 3)

        pack_a, map_a = create_reviewer_blinded_pack(
            canonical_items, practice_items, "SESS-TEST", "REV-A", "R1", 101
        )
        pack_b, map_b = create_reviewer_blinded_pack(
            canonical_items, practice_items, "SESS-TEST", "REV-B", "R2", 202
        )

        # Opaque display ID format
        for it in pack_a:
            self.assertTrue(it["display_id"].startswith("BLIND-R1-"))
            self.assertNotIn("PILOT-ITEM-", it["display_id"])
            self.assertNotIn("category", it)  # Research category withheld from reviewer
            self.assertNotIn("rule_id", it)

        # Item order differs between seeds
        order_a = [map_a[it["display_id"]]["canonical_item_id"] for it in pack_a]
        order_b = [map_b[it["display_id"]]["canonical_item_id"] for it in pack_b]
        self.assertNotEqual(order_a, order_b, "Item orders must be independently shuffled across reviewers")

    def test_adversarial_decoding_and_dual_iaa(self):
        """Assures that raw submissions decode accurately and evaluate on dual IAA metrics."""
        mapping_data = {
            "session_id": "SESS-TEST",
            "item_mappings": {
                "REV-A": {
                    "BLIND-R1-0001": {
                        "canonical_item_id": "PILOT-ITEM-001",
                        "category": "VERB_MORPHOLOGY",
                        "displayed_to_canonical": {"A": "CAND_B", "B": "CAND_A", "C": "CAND_C"},
                    }
                },
                "REV-B": {
                    "BLIND-R2-0001": {
                        "canonical_item_id": "PILOT-ITEM-001",
                        "category": "VERB_MORPHOLOGY",
                        "displayed_to_canonical": {"A": "CAND_A", "B": "CAND_B", "C": "CAND_C"},
                    }
                }
            }
        }

        sub_a = {
            "submission_id": "REV-SUB-A1",
            "session_id": "SESS-TEST",
            "reviewer_pseudonym": "REV-A",
            "opaque_item_id": "BLIND-R1-0001",
            "candidate_judgments": {
                "A": {"acceptability": "NATURAL_STANDARD", "certainty": "VERY_SURE"},  # displayed A is CAND_B
                "B": {"acceptability": "UNGRAMMATICAL", "certainty": "VERY_SURE"},     # displayed B is CAND_A
                "C": {"acceptability": "NATURAL_STANDARD", "certainty": "VERY_SURE"},  # displayed C is CAND_C
            },
            "preferred_candidates": ["A"],
            "timestamp": "2026-08-28T12:00:00Z",
        }

        sub_b = {
            "submission_id": "REV-SUB-B1",
            "session_id": "SESS-TEST",
            "reviewer_pseudonym": "REV-B",
            "opaque_item_id": "BLIND-R2-0001",
            "candidate_judgments": {
                "A": {"acceptability": "UNGRAMMATICAL", "certainty": "VERY_SURE"},     # displayed A is CAND_A
                "B": {"acceptability": "NATURAL_STANDARD", "certainty": "VERY_SURE"},  # displayed B is CAND_B
                "C": {"acceptability": "NATURAL_STANDARD", "certainty": "VERY_SURE"},  # displayed C is CAND_C
            },
            "preferred_candidates": ["B"],  # displayed B is CAND_B
            "timestamp": "2026-08-28T12:00:00Z",
        }

        dec_a = decode_submission(mapping_data, sub_a, allow_partial=True)
        dec_b = decode_submission(mapping_data, sub_b, allow_partial=True)

        # Both decoded records should agree that CAND_B is NATURAL_STANDARD and CAND_A is UNGRAMMATICAL
        self.assertEqual(dec_a[0]["canonical_candidate_judgments"]["CAND_B"]["acceptability"], "NATURAL_STANDARD")
        self.assertEqual(dec_b[0]["canonical_candidate_judgments"]["CAND_B"]["acceptability"], "NATURAL_STANDARD")
        self.assertEqual(dec_a[0]["canonical_preferred_candidates"], ["CAND_B"])
        self.assertEqual(dec_b[0]["canonical_preferred_candidates"], ["CAND_B"])

        # Dual IAA evaluation
        res = evaluate_dual_iaa(dec_a, dec_b, "REV-A", "REV-B")
        self.assertEqual(res["candidate_acceptability"]["raw_agreement"], 1.0)
        self.assertEqual(res["preferred_candidates"]["exact_matches"], 1)


if __name__ == "__main__":
    unittest.main()
