"""
Unit tests for BLF Reversible Normalization and Conservative Text Cleaning.
"""

import unittest

from blf.pipeline.cleaning import ConservativeTextCleaner
from blf.pipeline.normalization import NormalizationRule, ReversibleNormalizer


class TestReversibleNormalization(unittest.TestCase):

    def setUp(self) -> None:
        self.normalizer = ReversibleNormalizer(normalize_terminal_period_to_dari=True)

    def test_nfc_normalization(self) -> None:
        # Decomposed form: Bengali Ka + Virama + SSA (ক + ্‌ + ষ)
        decomposed = "ক\u09CD\u09B7"
        normalized, steps = self.normalizer.normalize(decomposed)
        self.assertEqual(normalized, "ক্ষ")

    def test_reversibility(self) -> None:
        raw_text = "  সে   বইটি  পড়ে ।  "
        normalized, steps = self.normalizer.normalize(raw_text)
        reverted = self.normalizer.revert(normalized, steps)
        self.assertEqual(reverted, raw_text)

    def test_zwj_preservation_after_hasanta(self) -> None:
        # Legitimate ligature: র + ্‌ + ZWJ + য
        legitimate_ligature = "\u09B0\u09CD\u200D\u09AF"
        normalized, steps = self.normalizer.normalize(legitimate_ligature)
        self.assertIn("\u200D", normalized)

    def test_spurious_zwj_removal(self) -> None:
        # Spurious ZWJ between Latin letters: a + ZWJ + b
        spurious = "a\u200Db"
        normalized, steps = self.normalizer.normalize(spurious)
        self.assertEqual(normalized, "ab")
        rules_applied = [s.rule for s in steps]
        self.assertIn(NormalizationRule.ZWJ_ZWNJ_POLICY, rules_applied)

    def test_period_to_dari(self) -> None:
        raw_text = "আমি ভাত খাই."
        normalized, steps = self.normalizer.normalize(raw_text)
        self.assertTrue(normalized.endswith("।"))


class TestConservativeCleaning(unittest.TestCase):

    def setUp(self) -> None:
        self.cleaner = ConservativeTextCleaner()

    def test_strips_control_characters(self) -> None:
        text_with_null = "বাংলা\x00ভাষা\x08পরীক্ষা"
        cleaned, metrics = self.cleaner.clean(text_with_null)
        self.assertEqual(cleaned, "বাংলাভাষাপরীক্ষা")
        self.assertEqual(metrics.removed_control_chars_count, 2)

    def test_preserves_bengali_diacritics(self) -> None:
        # Hasanta, Chandrabindu, Anusvara, Visarga, Nukta
        complex_bengali = "চাঁদ রঙ দুঃখ ডালিম ড় ঢ়"
        cleaned, metrics = self.cleaner.clean(complex_bengali)
        self.assertEqual(cleaned, complex_bengali)
        self.assertGreater(metrics.bengali_ratio, 0.7)


if __name__ == "__main__":
    unittest.main()
