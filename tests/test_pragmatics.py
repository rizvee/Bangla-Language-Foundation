"""
Unit tests for BLF Pragmatics, Social Deixis, and Dialogue Acts.
"""

import json
import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from blf.linguistics.pragmatics import PragmaticsEngine, HonorificTier, Register
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
        # 1. Honorific tier (Apni bolun / bolen)
        res_hon = self.engine.transform_addressee_register("বল", "PRES_SIMP", HonorificTier.HONORIFIC)
        self.assertEqual(res_hon, "আপনি বলেন")

        # 2. Familiar tier (Tumi bolo)
        res_fam = self.engine.transform_addressee_register("বল", "PRES_SIMP", HonorificTier.FAMILIAR)
        self.assertEqual(res_fam, "তুমি বলো")

        # 3. Intimate tier (Tui bolish)
        res_int = self.engine.transform_addressee_register("বল", "PRES_SIMP", HonorificTier.INTIMATE)
        self.assertEqual(res_int, "তুই বলিস")

        # 4. Future tense transform with object NP
        res_fut_hon = self.engine.transform_addressee_register(
            "কর", "FUT_SIMP", HonorificTier.HONORIFIC, object_np="কাজটা"
        )
        self.assertEqual(res_fut_hon, "আপনি কাজটা করবেন")

    def test_ki_disambiguation(self):
        # Polar particle 'কি'
        res_polar = self.engine.disambiguate_ki("তুমি কি খাবে?")
        types = [d["type"] for d in res_polar["disambiguations"]]
        self.assertIn("POLAR_INTERROGATIVE_PARTICLE", types)

        # Content Wh-pronoun 'কী'
        res_wh = self.engine.disambiguate_ki("তুমি কী খাবে?")
        types_wh = [d["type"] for d in res_wh["disambiguations"]]
        self.assertIn("INTERROGATIVE_PRONOUN_SUBSTANTIVE", types_wh)

        # Declinable substantive Wh-pronoun 'কিসের'
        res_gen = self.engine.disambiguate_ki("কিসের জন্য?")
        types_gen = [d["type"] for d in res_gen["disambiguations"]]
        self.assertIn("INTERROGATIVE_PRONOUN_SUBSTANTIVE", types_gen)

    def test_focus_clitic_attachment(self):
        # Restrictive clitic -i
        res_i = self.engine.attach_focus_clitic("আমি", "ই")
        self.assertEqual(res_i, "আমিই")

        # Additive clitic -o
        res_o = self.engine.attach_focus_clitic("তুমিও", "ও")
        self.assertIn("ও", res_o)


if __name__ == "__main__":
    unittest.main()
