"""
Unit tests for BLF Complex Predicate Engine, Vector Verbs & LVCs.
"""

import json
import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from blf.linguistics.complex_predicates import ComplexPredicateEngine, VECTOR_INVENTORY
from blf.validation.validators import load_schema, validate_dict_against_schema
CPRED_PATH = ROOT_DIR / "ontology" / "complex_predicates" / "complex_predicates.json"
SCHEMA_PATH = ROOT_DIR / "schemas" / "v0_1" / "complex_predicate.schema.json"


class TestComplexPredicates(unittest.TestCase):
    def setUp(self):
        self.engine = ComplexPredicateEngine()
        self.schema = load_schema(SCHEMA_PATH)
        with open(CPRED_PATH, "r", encoding="utf-8") as f:
            self.catalog = json.load(f)

    def test_schema_conformance(self):
        for cp in self.catalog["complex_predicates"]:
            pid = cp.get("predicate_id")
            valid, errors = validate_dict_against_schema(cp, self.schema)
            self.assertTrue(valid, f"Complex predicate {pid} failed schema: {errors}")

    def test_vector_verb_realization(self):
        # 1. Telic completion with phela: kheye phello
        res_fel = self.engine.realize_compound_verb("খা", "ফেলা", "PAST_SIMP.3_ORD")
        self.assertEqual(res_fel, "খেয়ে ফেলল")

        # 2. Cognitive achievement with phela: jene phello / bujhe phellam
        res_jene = self.engine.realize_compound_verb("জান", "ফেলা", "PAST_SIMP.3_ORD")
        self.assertEqual(res_jene, "জেনে ফেলল")

        res_bujhe = self.engine.realize_compound_verb("বোঝ", "ফেলা", "PAST_SIMP.1")
        self.assertEqual(res_bujhe, "বুঝে ফেললাম")

        # 3. Self-benefactive with neoa: kine nilam
        res_ne = self.engine.realize_compound_verb("কিনা", "নেওয়া", "PAST_SIMP.1")
        self.assertEqual(res_ne, "কিনে নিলাম")

        # 4. Other-benefactive with dewa: likhe dilo
        res_de = self.engine.realize_compound_verb("লিখ", "দেওয়া", "PAST_SIMP.3_ORD")
        self.assertEqual(res_de, "লিখে দিল")

        # 5. Inceptive with utha: heshe uthlo
        res_uth = self.engine.realize_compound_verb("হাস", "উঠা", "PAST_SIMP.3_ORD")
        self.assertEqual(res_uth, "হেসে উঠল")

    def test_light_verb_realization(self):
        # 1. Transitive LVC with kora: kaj korlam
        res_kor = self.engine.realize_light_verb_construction("কাজ", "করা", "PAST_SIMP.1")
        self.assertEqual(res_kor, "কাজ করলাম")

        # 2. Inchoative LVC with howa: shuru holo (exact form verification)
        res_ho = self.engine.realize_light_verb_construction("শুরু", "হওয়া", "PAST_SIMP.3_ORD")
        self.assertEqual(res_ho, "শুরু হলো")

        # 3. Experiencer LVC with paowa: khide pelo / khide paowa
        res_pao = self.engine.realize_light_verb_construction("ক্ষিদে", "পাওয়া", "PRES_SIMP.3_ORD")
        self.assertEqual(res_pao, "ক্ষিদে পায়")

    def test_selectional_restriction_validation(self):
        # Valid: dynamic transitive with phela
        valid_dyn, _ = self.engine.validate_vector_combination("খা", "ফেলা", "TRANSITIVE_DYNAMIC")
        self.assertTrue(valid_dyn)

        # Valid: cognitive achievement with phela (jene phela, bujhe phela)
        valid_cog, _ = self.engine.validate_vector_combination("জান", "ফেলা", "COGNITIVE_ACHIEVEMENT")
        self.assertTrue(valid_cog)

        # Invalid: pure stative posture with phela (*theke phela)
        invalid, err = self.engine.validate_vector_combination("থাক", "ফেলা", "STATIVE_POSTURE")
        self.assertFalse(invalid)
        self.assertIn("Selectional restriction violation", err)


if __name__ == "__main__":
    unittest.main()
