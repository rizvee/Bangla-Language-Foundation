"""
Adversarial Mutation and Cross-Layer Invariant Tests — BLF.

Adversarially tests that illegal combinations, broken provenance, and
unattested morphotactic patterns are strictly rejected by the BLF engines.
"""

import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from blf.generation.realizer import ConstrainedRealizer, RealizationError
from blf.linguistics.complex_predicates import ComplexPredicateEngine
from blf.linguistics.morphology.verbal_conjugator import VerbalConjugatorEngine, ConjugationError
from blf.linguistics.pragmatics import PragmaticsEngine, HonorificTier


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
        # Honorific Apni must yield -en / -un, never intimate -is
        apni_pres = self.prag_engine.transform_addressee_register("কর", "PRES_SIMP", HonorificTier.HONORIFIC)
        self.assertIn("করেন", apni_pres)
        self.assertNotIn("করিস", apni_pres)
        self.assertNotIn("করো", apni_pres)

        # Intimate Tui must yield -is, never honorific -en
        tui_pres = self.prag_engine.transform_addressee_register("কর", "PRES_SIMP", HonorificTier.INTIMATE)
        self.assertIn("করিস", tui_pres)
        self.assertNotIn("করেন", tui_pres)


if __name__ == "__main__":
    unittest.main()
