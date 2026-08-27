"""
Unit tests for Research Source Registry.
"""

import unittest
import json
from pathlib import Path
import sys

# Ensure src is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from blf.validation.validators import load_schema, validate_dict_against_schema


class TestSourceRegistry(unittest.TestCase):
    def setUp(self):
        self.root_dir = Path(__file__).parent.parent
        self.registry_path = self.root_dir / "sources" / "registry" / "sources.json"
        self.schema_path = self.root_dir / "schemas" / "v0_1" / "source.schema.json"

        self.source_schema = load_schema(self.schema_path)
        with open(self.registry_path, "r", encoding="utf-8") as f:
            self.registry = json.load(f)

    def test_all_sources_conform_to_schema(self):
        sources = self.registry.get("sources", [])
        self.assertGreater(len(sources), 0, "Source registry must not be empty.")

        seen_ids = set()
        for src in sources:
            sid = src.get("source_id")
            self.assertNotIn(sid, seen_ids, f"Duplicate source ID found: {sid}")
            seen_ids.add(sid)

            valid, errors = validate_dict_against_schema(src, self.source_schema)
            self.assertTrue(valid, f"Source '{sid}' failed schema validation: {errors}")

    def test_mandatory_citation_and_license(self):
        for src in self.registry.get("sources", []):
            self.assertTrue(bool(src.get("citation")), f"Source {src.get('source_id')} missing citation")
            self.assertTrue(bool(src.get("license")), f"Source {src.get('source_id')} missing license")


if __name__ == "__main__":
    unittest.main()
