"""
Unit tests for BLF Semantic Frames catalog and domain models.
"""

import json
import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

from blf.ontology.frames import SemanticFrame, SemanticRole, FrameType, FrameRelationType
from blf.validation.validators import load_schema, validate_dict_against_schema

FRAMES_PATH = ROOT_DIR / "ontology" / "frames" / "core_frames.json"
SCHEMA_PATH = ROOT_DIR / "schemas" / "v0_1" / "semantic_frame.schema.json"


class TestSemanticFrames(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema(SCHEMA_PATH)
        with open(FRAMES_PATH, "r", encoding="utf-8") as f:
            self.catalog = json.load(f)

    def test_catalog_structure(self):
        self.assertIn("frames", self.catalog)
        self.assertGreaterEqual(len(self.catalog["frames"]), 24)

    def test_frame_schema_conformance(self):
        for f in self.catalog["frames"]:
            fid = f.get("frame_id")
            valid, errors = validate_dict_against_schema(f, self.schema)
            self.assertTrue(valid, f"Frame {fid} failed schema: {errors}")

    def test_core_frame_domains_present(self):
        types_present = {f["frame_type"] for f in self.catalog["frames"]}
        expected_types = {
            "CORE_COMMUNICATION",
            "EVERYDAY_EVENT",
            "STATIVE_RELATIONAL",
            "COGNITIVE_EXPERIENCE",
            "PHYSICAL_ACTION",
            "SOCIAL_INTERACTION",
        }
        for et in expected_types:
            self.assertIn(et, types_present, f"Missing frame domain type: {et}")


if __name__ == "__main__":
    unittest.main()
