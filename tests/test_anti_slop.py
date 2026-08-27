"""
Unit tests for Anti-AI-Slop Linter.
"""

import unittest
from pathlib import Path
import tempfile
import sys

# Ensure scripts directory is accessible
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from check_anti_slop import scan_file


class TestAntiSlop(unittest.TestCase):
    def test_clean_text_passes(self):
        clean_content = """# Linguistic Evidence
We analyze the distribution of compound verbs in Bangladesh Standard Bangla.
Data was extracted from the 2012 Bangla Academy Grammar manual.
"""
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".md", encoding="utf-8") as tmp:
            tmp.write(clean_content)
            tmp_path = Path(tmp.name)

        try:
            violations = scan_file(tmp_path)
            self.assertEqual(len(violations), 0, f"Clean text should have 0 violations, got: {violations}")
        finally:
            tmp_path.unlink()

    def test_slop_phrases_detected(self):
        slop_content = """# Overview
In today's rapidly evolving digital landscape, we delve into the dataset.
This groundbreaking methodology plays a crucial role and is a testament to our team.
It is important to note that this is not only efficient but also robust.
"""
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".md", encoding="utf-8") as tmp:
            tmp.write(slop_content)
            tmp_path = Path(tmp.name)

        try:
            violations = scan_file(tmp_path)
            self.assertGreater(len(violations), 0, "Slop text should trigger violations.")
            reasons = [v[2] for v in violations]
            self.assertTrue(any("delve" in r for r in reasons))
            self.assertTrue(any("crucial" in r for r in reasons))
        finally:
            tmp_path.unlink()


if __name__ == "__main__":
    unittest.main()
