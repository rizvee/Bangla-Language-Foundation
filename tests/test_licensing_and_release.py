"""
Unit tests for Licensing Matrix, Release Manifest, and Publication Infrastructure.
"""

import json
from pathlib import Path
import unittest


class TestLicensingAndRelease(unittest.TestCase):

    def setUp(self) -> None:
        self.root_dir = Path(__file__).resolve().parent.parent
        self.matrix_path = self.root_dir / "sources" / "licensing" / "redistribution_matrix.json"
        self.sources_path = self.root_dir / "sources" / "registry" / "sources.json"
        self.manifest_path = self.root_dir / "release" / "release_manifest.json"
        self.license_decision_path = self.root_dir / "docs" / "DATA_LICENSE_DECISION.md"
        self.paper_skeleton_path = self.root_dir / "papers" / "methodology_paper_skeleton.md"

    def test_redistribution_matrix_integrity(self) -> None:
        self.assertTrue(self.matrix_path.is_file(), "Redistribution matrix file missing")
        with open(self.matrix_path, "r", encoding="utf-8") as f:
            matrix_data = json.load(f)

        with open(self.sources_path, "r", encoding="utf-8") as f:
            sources_data = json.load(f)

        source_ids = {s["source_id"] for s in sources_data.get("sources", [])}
        matrix_ids = {m["source_id"] for m in matrix_data.get("sources", [])}

        # Check that every registered source is represented in the matrix
        missing_in_matrix = source_ids - matrix_ids
        self.assertEqual(len(missing_in_matrix), 0, f"Sources missing in redistribution matrix: {missing_in_matrix}")

        # Check quarantined sources cannot be redistributed
        for entry in matrix_data.get("sources", []):
            if "Quarantined" in entry.get("spdx_license", ""):
                self.assertFalse(
                    entry.get("redistribution_allowed"),
                    f"Quarantined source {entry['source_id']} must have redistribution_allowed=False",
                )

    def test_release_manifest_invariants(self) -> None:
        self.assertTrue(self.manifest_path.is_file(), "Release manifest missing")
        with open(self.manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        # Invariant checks
        self.assertFalse(manifest.get("public_release_published"))
        self.assertEqual(manifest.get("gold_gate_status"), "READY_FOR_CONTROLLED_HUMAN_REVIEW_PILOT")
        self.assertEqual(manifest.get("epistemic_invariants", {}).get("total_gold_records"), 0)
        self.assertEqual(manifest.get("epistemic_invariants", {}).get("total_production_records"), 0)

    def test_data_license_decision_status(self) -> None:
        self.assertTrue(self.license_decision_path.is_file())
        with open(self.license_decision_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("DECISION_PENDING", content)

    def test_methodology_paper_skeleton_present(self) -> None:
        self.assertTrue(self.paper_skeleton_path.is_file())
        with open(self.paper_skeleton_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("EMPIRICAL PILOT PENDING", content)


if __name__ == "__main__":
    unittest.main()
