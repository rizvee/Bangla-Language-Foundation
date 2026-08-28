"""
Unit tests for the BLF Morphosyntactic & Inflectional Paradigm Engine.

Verifies:
1. Nominal declension engine across case allomorphy, classifiers, animacy, and number.
2. Pronominal declension paradigms across person, honorificity, and deixis.
3. Verbal conjugation engine across regular, vowel-mutating, and irregular verb roots.
4. Correctness of generated surface forms matching BDSB standards.
"""

import unittest
from pathlib import Path
import sys

# Ensure src is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from blf.linguistics.morphology import (
    NominalDeclensionEngine,
    PronominalParadigmEngine,
    VerbalConjugatorEngine,
    is_vowel_final,
    get_genitive_suffix,
    get_locative_suffix,
)


class TestNominalDeclension(unittest.TestCase):
    def setUp(self):
        self.engine = NominalDeclensionEngine()

    def test_vowel_detection(self):
        self.assertTrue(is_vowel_final("বাড়ি"))
        self.assertTrue(is_vowel_final("ঢাকা"))
        self.assertTrue(is_vowel_final("বই"))
        self.assertFalse(is_vowel_final("মানুষ"))
        self.assertFalse(is_vowel_final("কলম"))
        self.assertFalse(is_vowel_final("শিক্ষক"))

    def test_case_allomorphy_suffixes(self):
        self.assertEqual(get_genitive_suffix("মানুষ"), "ের")
        self.assertEqual(get_genitive_suffix("বাড়ি"), "র")
        self.assertEqual(get_locative_suffix("মানুষ"), "ে")
        self.assertEqual(get_locative_suffix("বাড়ি"), "তে")
        self.assertEqual(get_locative_suffix("ঢাকা"), "য়")

    def test_human_noun_declension(self):
        cells = self.engine.decline_noun("মানুষ", is_human=True, classifier="টি")
        self.assertEqual(cells["NOM.SG.INDEF"], "মানুষ")
        self.assertEqual(cells["ACC.SG.INDEF"], "মানুষকে")
        self.assertEqual(cells["GEN.SG.INDEF"], "মানুষের")
        self.assertEqual(cells["LOC.SG.INDEF"], "মানুষে")
        self.assertEqual(cells["NOM.SG.DEF"], "মানুষটি")
        self.assertEqual(cells["ACC.SG.DEF"], "মানুষটিকে")
        self.assertEqual(cells["GEN.SG.DEF"], "মানুষটির")
        self.assertEqual(cells["LOC.SG.DEF"], "মানুষটিতে")
        self.assertEqual(cells["NOM.PL.INDEF"], "মানুষেরা")
        self.assertEqual(cells["ACC.PL.INDEF"], "মানুষদেরকে")
        self.assertEqual(cells["GEN.PL.INDEF"], "মানুষদের")

    def test_inanimate_noun_declension(self):
        cells = self.engine.decline_noun("বই", is_human=False, classifier="টা")
        self.assertEqual(cells["NOM.SG.INDEF"], "বই")
        self.assertEqual(cells["ACC.SG.INDEF"], "বই")  # DOM: Inanimate direct object is unmarked
        self.assertEqual(cells["GEN.SG.INDEF"], "বইয়ের")
        self.assertEqual(cells["NOM.SG.DEF"], "বইটা")
        self.assertEqual(cells["ACC.SG.DEF"], "বইটা")
        self.assertEqual(cells["GEN.SG.DEF"], "বইটার")
        self.assertEqual(cells["LOC.SG.DEF"], "বইটাতে")
        self.assertEqual(cells["NOM.PL.INDEF"], "বইগুলো")
        self.assertEqual(cells["ACC.PL.INDEF"], "বইগুলো")
        self.assertEqual(cells["GEN.PL.INDEF"], "বইগুলোর")

    def test_classifier_plural_exclusivity(self):
        """Verifies that nominal declension never generates illegal stacked classifier+plural affixes."""
        human_cells = self.engine.decline_noun("মানুষ", is_human=True, classifier="টি")
        inanim_cells = self.engine.decline_noun("বই", is_human=False, classifier="টা")

        for key, form in {**human_cells, **inanim_cells}.items():
            self.assertNotIn("টাগুলো", form, f"Illegal stacked classifier+plural in {key}: {form}")
            self.assertNotIn("টিরা", form, f"Illegal stacked classifier+plural in {key}: {form}")
            self.assertNotIn("টাদের", form, f"Illegal stacked classifier+plural in {key}: {form}")


class TestPronominalParadigms(unittest.TestCase):
    def setUp(self):
        self.engine = PronominalParadigmEngine()

    def test_1st_person_forms(self):
        p_sg = self.engine.get_pronominal_paradigm("PRON-1-SG")
        self.assertIsNotNone(p_sg)
        self.assertEqual(p_sg["NOM"], "আমি")
        self.assertEqual(p_sg["ACC"], "আমাকে")
        self.assertEqual(p_sg["GEN"], "আমার")

        p_pl = self.engine.get_pronominal_paradigm("PRON-1-PL")
        self.assertIsNotNone(p_pl)
        self.assertEqual(p_pl["NOM"], "আমরা")
        self.assertEqual(p_pl["GEN"], "আমাদের")

    def test_2nd_person_honorific_tiers(self):
        p_hon = self.engine.get_pronominal_paradigm("PRON-2-HON-SG")
        p_fam = self.engine.get_pronominal_paradigm("PRON-2-FAM-SG")
        p_int = self.engine.get_pronominal_paradigm("PRON-2-INT-SG")

        self.assertEqual(p_hon["NOM"], "আপনি")
        self.assertEqual(p_hon["ACC"], "আপনাকে")
        self.assertEqual(p_hon["GEN"], "আপনার")

        self.assertEqual(p_fam["NOM"], "তুমি")
        self.assertEqual(p_fam["ACC"], "তোমাকে")
        self.assertEqual(p_fam["GEN"], "তোমার")

        self.assertEqual(p_int["NOM"], "তুই")
        self.assertEqual(p_int["ACC"], "তোকে")
        self.assertEqual(p_int["GEN"], "তোর")

    def test_3rd_person_deictic_and_honorific(self):
        p_dist_hon = self.engine.get_pronominal_paradigm("PRON-3-DIST-HON-SG")
        self.assertEqual(p_dist_hon["NOM"], "তিনি")
        self.assertEqual(p_dist_hon["ACC"], "তাঁকে")
        self.assertEqual(p_dist_hon["GEN"], "তাঁর")

        p_dist_ord = self.engine.get_pronominal_paradigm("PRON-3-DIST-ORD-SG")
        self.assertEqual(p_dist_ord["NOM"], "সে")
        self.assertEqual(p_dist_ord["ACC"], "তাকে")
        self.assertEqual(p_dist_ord["GEN"], "তার")


class TestVerbalConjugator(unittest.TestCase):
    def setUp(self):
        self.engine = VerbalConjugatorEngine()

    def test_regular_closed_root_kor(self):
        cells = self.engine.conjugate_root("কর")
        self.assertEqual(cells["PRES_SIMP.1"], "করি")
        self.assertEqual(cells["PRES_SIMP.2_ORD"], "করো")
        self.assertEqual(cells["PRES_SIMP.2_HON"], "করেন")
        self.assertEqual(cells["PRES_SIMP.2_INT"], "করিস")
        self.assertEqual(cells["PRES_SIMP.3_ORD"], "করে")
        self.assertEqual(cells["PRES_SIMP.3_HON"], "করেন")
        self.assertEqual(cells["PRES_CONT.1"], "করছি")
        self.assertEqual(cells["PAST_SIMP.1"], "করলাম")
        self.assertEqual(cells["PAST_CONT.1"], "করছিলাম")
        self.assertEqual(cells["PAST_HAB.1"], "করতাম")
        self.assertEqual(cells["FUT_SIMP.1"], "করব")
        self.assertEqual(cells["FUT_SIMP.2_HON"], "করবেন")
        self.assertEqual(cells["IMP.2_HON"], "করুন")
        self.assertEqual(cells["NF_CONJUNCTIVE"], "করে")
        self.assertEqual(cells["NF_CONDITIONAL"], "করলে")
        self.assertEqual(cells["NF_INFINITIVE"], "করতে")

    def test_irregular_root_ja(self):
        cells = self.engine.conjugate_root("যা")
        self.assertEqual(cells["PRES_SIMP.1"], "যাই")
        self.assertEqual(cells["PRES_CONT.1"], "যাচ্ছি")
        self.assertEqual(cells["PAST_SIMP.1"], "গেলাম")
        self.assertEqual(cells["PAST_SIMP.3_ORD"], "গেল")
        self.assertEqual(cells["PAST_PERF.1"], "গিয়েছিলাম")
        self.assertEqual(cells["PAST_HAB.1"], "যেতাম")
        self.assertEqual(cells["FUT_SIMP.1"], "যাব")
        self.assertEqual(cells["NF_CONJUNCTIVE"], "গিয়ে")
        self.assertEqual(cells["NF_CONDITIONAL"], "গেলে")

    def test_vowel_mutation_roots(self):
        de_cells = self.engine.conjugate_root("দে")
        self.assertEqual(de_cells["PRES_SIMP.1"], "দিই")
        self.assertEqual(de_cells["PRES_SIMP.2_ORD"], "দাও")
        self.assertEqual(de_cells["PRES_SIMP.3_ORD"], "দেয়")
        self.assertEqual(de_cells["PAST_SIMP.1"], "দিলাম")
        self.assertEqual(de_cells["FUT_SIMP.1"], "দেব")
        self.assertEqual(de_cells["IMP.2_HON"], "দিন")

        kha_cells = self.engine.conjugate_root("খা")
        self.assertEqual(kha_cells["PRES_SIMP.1"], "খাই")
        self.assertEqual(kha_cells["PRES_CONT.1"], "খাচ্ছি")
        self.assertEqual(kha_cells["PAST_SIMP.1"], "খেলাম")
        self.assertEqual(kha_cells["FUT_SIMP.1"], "খাব")
        self.assertEqual(kha_cells["NF_CONJUNCTIVE"], "খেয়ে")

    def test_irregular_root_ho(self):
        """Regression test verifying exact forms of irregular verb root 'হ' (howa)."""
        ho_cells = self.engine.conjugate_root("হ")
        self.assertEqual(ho_cells["PRES_SIMP.1"], "হই")
        self.assertEqual(ho_cells["PRES_SIMP.2_ORD"], "হও")
        self.assertEqual(ho_cells["PRES_SIMP.2_HON"], "হন")
        self.assertEqual(ho_cells["PRES_SIMP.2_INT"], "হস")
        self.assertEqual(ho_cells["PRES_SIMP.3_ORD"], "হয়")
        self.assertEqual(ho_cells["PRES_SIMP.3_HON"], "হন")
        self.assertEqual(ho_cells["PRES_CONT.1"], "হচ্ছি")
        self.assertEqual(ho_cells["PRES_CONT.3_ORD"], "হচ্ছে")
        self.assertEqual(ho_cells["PRES_PERF.1"], "হয়েছি")
        self.assertEqual(ho_cells["PRES_PERF.3_ORD"], "হয়েছে")
        self.assertEqual(ho_cells["PAST_SIMP.1"], "হলাম")
        self.assertEqual(ho_cells["PAST_SIMP.3_ORD"], "হলো")
        self.assertEqual(ho_cells["PAST_CONT.1"], "হচ্ছিলাম")
        self.assertEqual(ho_cells["PAST_HAB.1"], "হতাম")
        self.assertEqual(ho_cells["PAST_PERF.1"], "হয়েছিলাম")
        self.assertEqual(ho_cells["FUT_SIMP.1"], "হব")
        self.assertEqual(ho_cells["FUT_SIMP.2_HON"], "হবেন")
        # Explicit distinction between Indicative 'হন' and Imperative 'হোন'
        self.assertEqual(ho_cells["IMP.2_HON"], "হোন")
        self.assertNotEqual(ho_cells["IMP.2_HON"], ho_cells["PRES_SIMP.2_HON"])
        self.assertEqual(ho_cells["NF_CONJUNCTIVE"], "হয়ে")
        self.assertEqual(ho_cells["NF_CONDITIONAL"], "হলে")
        self.assertEqual(ho_cells["NF_INFINITIVE"], "হতে")

    def test_negative_conjugation_polarity(self):
        """Verifies perfective negation with past stem + -ni vs general postverbal na."""
        # Present Perfect -> past stem + -ni
        self.assertEqual(self.engine.conjugate_negative("কর", "PRES_PERF.1"), "করিনি")
        self.assertEqual(self.engine.conjugate_negative("কর", "PRES_PERF.3_ORD"), "করেনি")
        self.assertEqual(self.engine.conjugate_negative("যা", "PRES_PERF.1"), "যাইনি")
        self.assertEqual(self.engine.conjugate_negative("যা", "PRES_PERF.3_ORD"), "যায়নি")
        self.assertEqual(self.engine.conjugate_negative("খা", "PRES_PERF.1"), "খাইনি")
        self.assertEqual(self.engine.conjugate_negative("খা", "PRES_PERF.3_ORD"), "খায়নি")
        self.assertEqual(self.engine.conjugate_negative("হ", "PRES_PERF.3_ORD"), "হয়নি")
        self.assertEqual(self.engine.conjugate_negative("বল", "PRES_PERF.3_ORD"), "বলেনি")
        self.assertEqual(self.engine.conjugate_negative("দেখ", "PRES_PERF.3_ORD"), "দেখেনি")
        # Calibrated 1st person standard forms
        self.assertEqual(self.engine.conjugate_negative("দে", "PRES_PERF.1"), "দিইনি")
        self.assertEqual(self.engine.conjugate_negative("নে", "PRES_PERF.1"), "নিইনি")
        self.assertEqual(self.engine.conjugate_negative("শেখ", "PRES_PERF.1"), "শিখিনি")

        # Other tenses -> finite verb + na
        self.assertEqual(self.engine.conjugate_negative("কর", "PRES_SIMP.1"), "করি না")
        self.assertEqual(self.engine.conjugate_negative("কর", "FUT_SIMP.1"), "করব না")
        self.assertEqual(self.engine.conjugate_negative("যা", "FUT_SIMP.2_ORD"), "যাবে না")

        # Rejection of unmodeled verb roots to prevent arbitrary hallucination
        from blf.linguistics.morphology.verbal_conjugator import ConjugationError
        with self.assertRaises(ConjugationError):
            self.engine.conjugate_negative("অজানা_ধাতু", "PRES_PERF.1")


if __name__ == "__main__":
    unittest.main()
