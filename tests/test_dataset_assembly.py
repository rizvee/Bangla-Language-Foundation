"""
Unit tests for BLF Dataset Split Policy and Distribution Audit Framework.
"""

import unittest

from blf.dataset.distribution_audit import DistributionAuditor, QuotaSpecification
from blf.dataset.split_policy import FamilyGroupedSplitter, LeakageViolationError


class TestDatasetSplitPolicy(unittest.TestCase):

    def test_family_grouped_split_zero_leakage(self) -> None:
        # Create 10 families, 4 variants each = 40 records
        items = []
        for f_idx in range(10):
            fam_id = f"SF-{f_idx:03d}"
            for v_idx in range(4):
                items.append({
                    "item_id": f"ITEM-{f_idx:03d}-{v_idx}",
                    "sentence_family_id": fam_id,
                    "text": f"Variant {v_idx} of family {f_idx}",
                })

        splitter = FamilyGroupedSplitter(train_ratio=0.7, dev_ratio=0.15, test_ratio=0.15, seed=42)
        res = splitter.split(items)

        # Check disjoint sets of families
        self.assertEqual(len(res.train_family_ids & res.dev_family_ids), 0)
        self.assertEqual(len(res.train_family_ids & res.test_family_ids), 0)
        self.assertEqual(len(res.dev_family_ids & res.test_family_ids), 0)

        # Check that total families equal 10
        total_assigned_fams = len(res.train_family_ids) + len(res.dev_family_ids) + len(res.test_family_ids)
        self.assertEqual(total_assigned_fams, 10)

        # Check that items in each split only come from the assigned families
        for it in res.train_items:
            self.assertIn(it["sentence_family_id"], res.train_family_ids)
        for it in res.dev_items:
            self.assertIn(it["sentence_family_id"], res.dev_family_ids)
        for it in res.test_items:
            self.assertIn(it["sentence_family_id"], res.test_family_ids)

    def test_leakage_detection_raises_error(self) -> None:
        splitter = FamilyGroupedSplitter()
        res = splitter.split([])
        # Artificially inject overlapping family id
        res.train_family_ids.add("SF-OVERLAP")
        res.test_family_ids.add("SF-OVERLAP")
        with self.assertRaises(LeakageViolationError):
            res.verify_no_leakage()


class TestDistributionAuditor(unittest.TestCase):

    def test_balanced_distribution_passes(self) -> None:
        records = [
            {"register": "formal_standard", "variety": "bdsb_standard", "frame_id": "F1", "construction_id": "C1"},
            {"register": "colloquial_standard", "variety": "dhaka_colloquial", "frame_id": "F2", "construction_id": "C2"},
            {"register": "intimate_conversational", "variety": "sylheti", "frame_id": "F3", "construction_id": "C3"},
            {"register": "social_chat_shorthand", "variety": "bdsb_standard", "frame_id": "F4", "construction_id": "C4"},
            {"register": "formal_standard", "variety": "chittagonian", "frame_id": "F5", "construction_id": "C5"},
        ]
        spec = QuotaSpecification(min_registers_count=4, min_dialects_count=3, min_frames_count=5, min_constructions_count=5)
        auditor = DistributionAuditor(spec)
        report = auditor.audit(records)

        self.assertTrue(report.passed_quotas)
        self.assertEqual(len(report.violations), 0)

    def test_deficient_distribution_reports_violations(self) -> None:
        # Only 1 register, 1 dialect
        records = [
            {"register": "formal_standard", "variety": "bdsb_standard", "frame_id": "F1", "construction_id": "C1"},
            {"register": "formal_standard", "variety": "bdsb_standard", "frame_id": "F1", "construction_id": "C1"},
        ]
        spec = QuotaSpecification(min_registers_count=3, min_dialects_count=2, min_frames_count=3, min_constructions_count=3)
        auditor = DistributionAuditor(spec)
        report = auditor.audit(records)

        self.assertFalse(report.passed_quotas)
        self.assertGreater(len(report.violations), 0)


if __name__ == "__main__":
    unittest.main()
