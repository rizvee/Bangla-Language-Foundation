"""
Unit tests for Advanced Multi-Rater IAA Metrics (Fleiss' Kappa and Krippendorff's Alpha).
"""

import unittest

from blf.quality.advanced_iaa import (
    InsufficientDataError,
    compute_fleiss_kappa,
    compute_krippendorff_alpha_nominal,
)


class TestAdvancedIAA(unittest.TestCase):

    def test_fleiss_kappa_perfect_agreement(self) -> None:
        # 3 items, 3 raters, all agree
        matrix = [
            ["ACCEPTABLE", "ACCEPTABLE", "ACCEPTABLE"],
            ["UNACCEPTABLE", "UNACCEPTABLE", "UNACCEPTABLE"],
            ["ACCEPTABLE", "ACCEPTABLE", "ACCEPTABLE"],
        ]
        kappa = compute_fleiss_kappa(matrix)
        self.assertEqual(kappa, 1.0)

    def test_fleiss_kappa_insufficient_data(self) -> None:
        with self.assertRaises(InsufficientDataError):
            compute_fleiss_kappa([])

        with self.assertRaises(InsufficientDataError):
            # Only 1 rater
            compute_fleiss_kappa([["A"], ["B"]])

    def test_fleiss_kappa_moderate_agreement(self) -> None:
        matrix = [
            ["A", "A", "B"],
            ["A", "A", "A"],
            ["B", "B", "A"],
            ["B", "B", "B"],
        ]
        kappa = compute_fleiss_kappa(matrix)
        self.assertGreater(kappa, 0.2)
        self.assertLessEqual(kappa, 1.0)

    def test_krippendorff_alpha_nominal_perfect(self) -> None:
        # 3 raters x 4 items
        data = [
            ["A", "B", "A", "B"],
            ["A", "B", "A", "B"],
            ["A", "B", "A", "B"],
        ]
        alpha = compute_krippendorff_alpha_nominal(data)
        self.assertEqual(alpha, 1.0)

    def test_krippendorff_alpha_with_missing_values(self) -> None:
        data = [
            ["A", "B", None, "B"],
            ["A", "B", "A", None],
            [None, "B", "A", "B"],
        ]
        alpha = compute_krippendorff_alpha_nominal(data)
        self.assertGreater(alpha, 0.5)

    def test_krippendorff_alpha_insufficient_data(self) -> None:
        with self.assertRaises(InsufficientDataError):
            compute_krippendorff_alpha_nominal([[]])


if __name__ == "__main__":
    unittest.main()
