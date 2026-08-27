"""
Unit tests for BLF Construction Grammar catalogs and domain models.
"""

import json
import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from blf.ontology.constructions import LinguisticConstruction, ConstructionType, WordOrder
from blf.validation.validators import load_schema, validate_dict_against_schema
CONSTRUCTIONS_PATH = ROOT_DIR / "ontology" / "constructions" / "constructions.json"
SCHEMA_PATH = ROOT_DIR / "schemas" / "v0_1" / "linguistic_construction.schema.json"


class TestConstructions(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema(SCHEMA_PATH)
        with open(CONSTRUCTIONS_PATH, "r", encoding="utf-8") as f:
            self.catalog = json.load(f)

    def test_catalog_structure(self):
        self.assertIn("constructions", self.catalog)
        self.assertGreaterEqual(len(self.catalog["constructions"]), 20)

    def test_construction_schema_conformance(self):
        for c in self.catalog["constructions"]:
            cid = c.get("construction_id")
            valid, errors = validate_dict_against_schema(c, self.schema)
            self.assertTrue(valid, f"Construction {cid} failed schema validation: {errors}")

    def test_core_construction_types_present(self):
        types_present = {c["construction_type"] for c in self.catalog["constructions"]}
        expected_types = {
            "DECLARATIVE_TRANSITIVE",
            "DECLARATIVE_INTRANSITIVE",
            "DECLARATIVE_DITRANSITIVE",
            "COPULAR_EQUATIVE",
            "EXISTENTIAL_POSSESSIVE",
            "EXPERIENCER_DATIVE_SUBJECT",
            "POLAR_INTERROGATIVE",
            "WH_INTERROGATIVE",
            "IMPERATIVE_DIRECT",
            "PROHIBITIVE_NEGATIVE",
            "COMPLEX_CONJUNCTIVE",
            "COMPLEX_CONDITIONAL",
            "COMPLEX_CORRELATIVE",
            "INFORMATION_TOPICALIZATION",
            "INFORMATION_PRODROP",
        }
        for et in expected_types:
            self.assertIn(et, types_present, f"Missing core construction type: {et}")


if __name__ == "__main__":
    unittest.main()
