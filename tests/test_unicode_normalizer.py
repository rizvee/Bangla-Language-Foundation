"""
Unit tests for Bengali Unicode Normalization.
"""

import unittest
import unicodedata
from pathlib import Path
import sys

# Ensure src is in sys.path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from blf.linguistics.normalizer import (
    normalize_bangla_text,
    contains_bengali_characters,
    get_bengali_character_ratio,
)


class TestUnicodeNormalizer(unittest.TestCase):
    def test_nfc_normalization(self):
        # Decomposed form vs Composed form
        text = "আমি বাংলায় গান গাই।"
        nfd_text = unicodedata.normalize("NFD", text)
        normalized = normalize_bangla_text(nfd_text)
        self.assertEqual(normalized, unicodedata.normalize("NFC", text))

    def test_whitespace_normalization(self):
        messy_text = "  ঢাকা   বিশ্ববিদ্যালয়   \t  "
        normalized = normalize_bangla_text(messy_text)
        expected = unicodedata.normalize("NFC", "ঢাকা বিশ্ববিদ্যালয়")
        self.assertEqual(normalized, expected)

    def test_bengali_character_detection(self):
        bangla_str = "ভাষা আন্দোলন"
        english_str = "Language Movement"
        mixed_str = "Bangla ভাষা"

        self.assertTrue(contains_bengali_characters(bangla_str))
        self.assertFalse(contains_bengali_characters(english_str))
        self.assertTrue(contains_bengali_characters(mixed_str))

    def test_bengali_ratio(self):
        pure_bangla = "বাংলা ভাষা"
        mixed = "Bangla ভাষা"
        ratio_pure = get_bengali_character_ratio(pure_bangla)
        ratio_mixed = get_bengali_character_ratio(mixed)

        self.assertEqual(ratio_pure, 1.0)
        self.assertGreater(ratio_mixed, 0.0)
        self.assertLess(ratio_mixed, 1.0)


if __name__ == "__main__":
    unittest.main()
