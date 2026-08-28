"""
Unit tests for BLF Pragmatics, Social Deixis, and Structured Interrogative Analyzer.
"""

import json
import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from blf.linguistics.pragmatics import PragmaticsEngine, HonorificTier, PRAGMATIC_PARTICLE_REGISTRY
from blf.validation.validators import load_schema, validate_dict_against_schema

DA_PATH = ROOT_DIR / "ontology" / "pragmatics" / "dialogue_acts.json"
SCHEMA_PATH = ROOT_DIR / "schemas" / "v0_1" / "dialogue_act.schema.json"


class TestPragmatics(unittest.TestCase):
    def setUp(self):
        self.engine = PragmaticsEngine()
        self.schema = load_schema(SCHEMA_PATH)
        with open(DA_PATH, "r", encoding="utf-8") as f:
            self.da_catalog = json.load(f)

    def test_dialogue_act_schema_conformance(self):
        for da in self.da_catalog["dialogue_acts"]:
            aid = da.get("act_id")
            valid, errors = validate_dict_against_schema(da, self.schema)
            self.assertTrue(valid, f"Dialogue act {aid} failed schema: {errors}")

    def test_social_deixis_register_transform(self):
        # 1. Honorific tier (Apni bolen)
        res_hon = self.engine.transform_addressee_register("বল", "PRES_SIMP", HonorificTier.HONORIFIC)
        self.assertEqual(res_hon, "আপনি বলেন")

        # 2. Ordinary tier (Tumi bolo)
        res_ord = self.engine.transform_addressee_register("বল", "PRES_SIMP", HonorificTier.ORDINARY)
        self.assertEqual(res_ord, "তুমি বলো")

        # 3. Intimate tier (Tui bolish)
        res_int = self.engine.transform_addressee_register("বল", "PRES_SIMP", HonorificTier.INTIMATE)
        self.assertEqual(res_int, "তুই বলিস")

        # 4. Future tense transform with object NP
        res_fut_hon = self.engine.transform_addressee_register(
            "কর", "FUT_SIMP", HonorificTier.HONORIFIC, object_np="কাজটা"
        )
        self.assertEqual(res_fut_hon, "আপনি কাজটা করবেন")

    def test_ki_disambiguation(self):
        # 1. Polar particle 'কি' with intransitive verb
        res_polar = self.engine.disambiguate_ki("তুমি কি যাবে?")
        funcs = [d["syntactic_function"] for d in res_polar["disambiguations"]]
        self.assertIn("POLAR_INTERROGATIVE_PARTICLE", funcs)
        self.assertEqual(res_polar["disambiguations"][0]["confidence"], "HIGH")

        # 2. Content Wh-pronoun 'কী'
        res_wh = self.engine.disambiguate_ki("তুমি কী খাবে?")
        funcs_wh = [d["syntactic_function"] for d in res_wh["disambiguations"]]
        self.assertIn("INTERROGATIVE_PRONOUN_SUBSTANTIVE", funcs_wh)

        # 3. Declinable substantive Wh-pronoun 'কিসের'
        res_gen = self.engine.disambiguate_ki("কিসের জন্য?")
        funcs_gen = [d["syntactic_function"] for d in res_gen["disambiguations"]]
        self.assertIn("INTERROGATIVE_PRONOUN_SUBSTANTIVE", funcs_gen)

        # 4. Transitive verb without overt object -> Wh-pronoun 'কী'
        res_raw = self.engine.disambiguate_ki("তুমি কি চাও?")
        dis = res_raw["disambiguations"][0]
        self.assertEqual(dis["syntactic_function"], "INTERROGATIVE_PRONOUN_SUBSTANTIVE")
        self.assertEqual(dis["normalized_standard_form"], "কী")

        # 5. Transitive verb with overt object -> Polar particle 'কি'
        res_obj = self.engine.disambiguate_ki("তুমি কি ভাত খাবে?")
        dis_obj = res_obj["disambiguations"][0]
        self.assertEqual(dis_obj["syntactic_function"], "POLAR_INTERROGATIVE_PARTICLE")
        self.assertEqual(dis_obj["normalized_standard_form"], "কি")

        # 6. Unknown verb root valency -> AMBIGUOUS fallback (never guessed)
        res_unknown = self.engine.disambiguate_ki("তুমি কি অজানাক্রিয়া?")
        dis_unk = res_unknown["disambiguations"][0]
        self.assertEqual(dis_unk["syntactic_function"], "AMBIGUOUS")
        self.assertEqual(dis_unk["confidence"], "LOW")
        self.assertTrue(dis_unk["review_required"])

    def test_focus_clitic_attachment(self):
        # Restrictive clitic -i
        res_i = self.engine.attach_focus_clitic("আমি", "ই")
        self.assertEqual(res_i, "আমিই")

        # Additive clitic -o
        res_o = self.engine.attach_focus_clitic("তুমি", "ও")
        self.assertEqual(res_o, "তুমিও")

    def test_polyfunctional_particle_definitions(self):
        self.assertIn("না", PRAGMATIC_PARTICLE_REGISTRY)
        self.assertIn("তো", PRAGMATIC_PARTICLE_REGISTRY)
        self.assertIn("যে", PRAGMATIC_PARTICLE_REGISTRY)
        self.assertIn("বা", PRAGMATIC_PARTICLE_REGISTRY)

        na_senses = [s.sense_id for s in PRAGMATIC_PARTICLE_REGISTRY["না"].senses]
        self.assertIn("SENSE-NA-NEGATION", na_senses)
        self.assertIn("SENSE-NA-CONFIRMATION-TAG", na_senses)


if __name__ == "__main__":
    unittest.main()
