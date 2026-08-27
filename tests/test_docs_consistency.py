"""
Unit tests for Documentation Consistency Checker.
"""

import unittest
from pathlib import Path
import tempfile
import sys

# Ensure scripts directory is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from check_docs_consistency import check_required_docs, check_file_content


class TestDocsConsistency(unittest.TestCase):
    def setUp(self):
        self.root_dir = Path(__file__).parent.parent

    def test_all_required_public_docs_exist(self):
        errors = check_required_docs(self.root_dir)
        self.assertEqual(len(errors), 0, f"Missing required docs: {errors}")

    def test_readme_and_docs_index_links_resolve(self):
        readme_path = self.root_dir / "README.md"
        errors, warnings = check_file_content(readme_path, self.root_dir)
        self.assertEqual(len(errors), 0, f"README has broken links or banned patterns: {errors}")

        docs_index_path = self.root_dir / "docs" / "index.md"
        errors, warnings = check_file_content(docs_index_path, self.root_dir)
        self.assertEqual(len(errors), 0, f"docs/index.md has broken links or banned patterns: {errors}")

    def test_broken_link_is_flagged(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".md", encoding="utf-8") as tmp:
            tmp.write("[Broken Link](non_existent_file_xyz.md)\n")
            tmp_path = Path(tmp.name)

        try:
            errors, warnings = check_file_content(tmp_path, tmp_path.parent)
            self.assertGreater(len(errors), 0)
            self.assertTrue(any("Broken relative link" in e for e in errors))
        finally:
            tmp_path.unlink()

    def test_local_file_scheme_is_flagged(self):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".md", encoding="utf-8") as tmp:
            tmp.write("[Local Link](file:///C:/Users/ADMIN/test.md)\n")
            tmp_path = Path(tmp.name)

        try:
            errors, warnings = check_file_content(tmp_path, tmp_path.parent)
            self.assertGreater(len(errors), 0)
            self.assertTrue(any("Local 'file:///'" in e for e in errors))
        finally:
            tmp_path.unlink()


if __name__ == "__main__":
    unittest.main()
