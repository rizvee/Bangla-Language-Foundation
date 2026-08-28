"""
Unit tests for BLF Pragmatics, Social Deixis, and Dialogue Acts.
"""

import json
import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from blf.linguistics.pragmatics import PragmaticsEngine, HonorificTier, Register, POLYFUNCTIONAL_PARTICLES
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
        # 1. Polar particle 'কি' with intransitive verb
        res_polar = self.engine.disambiguate_ki("তুমি কি যাবে?")
        funcs = [d["syntactic_function"] for d in res_polar["disambiguations"]]
        self.assertIn("POLAR_INTERROGATIVE_PARTICLE", funcs)

        # 2. Content Wh-pronoun 'কী'
        res_wh = self.engine.disambiguate_ki("তুমি কী খাবে?")
        funcs_wh = [d["syntactic_function"] for d in res_wh["disambiguations"]]
        self.assertIn("INTERROGATIVE_PRONOUN_SUBSTANTIVE", funcs_wh)

        # 3. Declinable substantive Wh-pronoun 'কিসের'
        res_gen = self.engine.disambiguate_ki("কিসের জন্য?")
        funcs_gen = [d["syntactic_function"] for d in res_gen["disambiguations"]]
        self.assertIn("INTERROGATIVE_PRONOUN_SUBSTANTIVE", funcs_gen)

        # 4. Raw non-standard digital spelling of Wh-pronoun 'কি' in argument position
        res_raw = self.engine.disambiguate_ki("তুমি কি চাও?")
        dis = res_raw["disambiguations"][0]
        self.assertEqual(dis["syntactic_function"], "INTERROGATIVE_PRONOUN_SUBSTANTIVE")
        self.assertEqual(dis["orthography_standard"], "NONSTANDARD_DIGITAL_SPELLING")
        self.assertEqual(dis["intended_standard_form"], "কী")

    def test_focus_clitic_attachment(self):
        # Restrictive clitic -i
        res_i = self.engine.attach_focus_clitic("আমি", "ই")
        self.assertEqual(res_i, "আমিই")

        # Additive clitic -o
        res_o = self.engine.attach_focus_clitic("তুমি", "ও")
        self.assertEqual(res_o, "তুমিও")

    def test_polyfunctional_particle_definitions(self):
        self.assertIn("না", POLYFUNCTIONAL_PARTICLES)
        self.assertIn("তো", POLYFUNCTIONAL_PARTICLES)
        self.assertIn("যে", POLYFUNCTIONAL_PARTICLES)
        self.assertIn("বা", POLYFUNCTIONAL_PARTICLES)
        
        na_senses = [s.sense_id for s in POLYFUNCTIONAL_PARTICLES["না"].senses]
        self.assertIn("SENSE-NA-NEGATOR", na_senses)
        self.assertIn("SENSE-NA-TAG-QUESTION", na_senses)
        self.assertIn("SENSE-NA-DIRECTIVE-SOFTENER", na_senses)


if __name__ == "__main__":
    unittest.main()
