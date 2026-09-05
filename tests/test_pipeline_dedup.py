"""
Unit tests for BLF 4-Tier Deduplication and Pipeline Manifest Tracking.
"""

import unittest

from blf.pipeline.deduplication import DeduplicationTier, MultiTierDeduplicator
from blf.pipeline.manifest import PipelineManifest, PipelineRecord


class TestMultiTierDeduplication(unittest.TestCase):

    def setUp(self) -> None:
        self.dedup = MultiTierDeduplicator(near_duplicate_threshold=0.80)

    def test_tier_1_exact_match(self) -> None:
        text = "তিনি প্রতিদিন সকালে হাঁটেন।"
        r1 = self.dedup.check_and_add("rec_1", text)
        self.assertFalse(r1.is_duplicate)
        self.assertEqual(r1.tier, DeduplicationTier.UNIQUE)

        r2 = self.dedup.check_and_add("rec_2", text)
        self.assertTrue(r2.is_duplicate)
        self.assertEqual(r2.tier, DeduplicationTier.TIER_1_EXACT)
        self.assertEqual(r2.duplicate_of, "rec_1")

    def test_tier_2_normalized_whitespace_match(self) -> None:
        text_a = "তিনি   প্রতিদিন  সকালে   হাঁটেন।"
        text_b = "তিনি প্রতিদিন সকালে হাঁটেন।"
        # First add text_a
        r1 = self.dedup.check_and_add("rec_a", text_a)
        self.assertFalse(r1.is_duplicate)

        # text_b differs in raw whitespace, but normalized match
        r2 = self.dedup.check_and_add("rec_b", text_b)
        self.assertTrue(r2.is_duplicate)
        self.assertEqual(r2.tier, DeduplicationTier.TIER_2_NORMALIZED)
        self.assertEqual(r2.duplicate_of, "rec_a")

    def test_tier_3_morpho_candidate_similarity(self) -> None:
        t1 = "ছেলেটি বল খেলছে।"
        t2 = "বালকটি বল খেলছে।"
        sig = "BOY-NOM BALL-ACC PLAY-PROG"

        r1 = self.dedup.check_and_add("rec_m1", t1, morpho_tag_sequence=sig)
        self.assertFalse(r1.is_duplicate)

        r2 = self.dedup.check_and_add("rec_m2", t2, morpho_tag_sequence=sig)
        # Identical POS sequence produces similarity flag, NOT automatic duplicate deletion
        self.assertFalse(r2.is_duplicate)
        self.assertTrue(r2.candidate_similarity)

    def test_tier_4_lexical_overlap_review_flag(self) -> None:
        t1 = "আমাদের গ্রামে অনেক সুন্দর সবুজ মাঠ এবং নদী আছে"
        t2 = "আমাদের গ্রামে অনেক সুন্দর সবুজ মাঠ এবং একটি নদী আছে"

        r1 = self.dedup.check_and_add("rec_s1", t1)
        self.assertFalse(r1.is_duplicate)

        r2 = self.dedup.check_and_add("rec_s2", t2)
        # Lexical overlap flags for review, never automatically deletes
        self.assertFalse(r2.is_duplicate)
        self.assertTrue(r2.requires_review)
        self.assertEqual(r2.tier, DeduplicationTier.TIER_4_LEXICAL_OVERLAP)

    def test_word_order_minimal_pairs_never_collapsed(self) -> None:
        # Canonical SOV vs Topicalized OSV
        sov = "আমি বই পড়ি"
        osv = "বই আমি পড়ি"

        r1 = self.dedup.check_and_add("rec_sov", sov)
        self.assertFalse(r1.is_duplicate)

        r2 = self.dedup.check_and_add("rec_osv", osv)
        self.assertFalse(r2.is_duplicate, "Word order permutations must never be collapsed as duplicates!")

    def test_minimal_pair_family_protection(self) -> None:
        # Polarity minimal pairs with high lexical overlap
        aff = "সে ভাত খায়"
        neg = "সে ভাত খায় না"

        r1 = self.dedup.check_and_add("rec_aff", aff, sentence_family_id="SF-001", minimal_pair_id="MP-01")
        self.assertFalse(r1.is_duplicate)

        r2 = self.dedup.check_and_add("rec_neg", neg, sentence_family_id="SF-001", minimal_pair_id="MP-01")
        self.assertFalse(r2.is_duplicate)
        self.assertFalse(r2.requires_review, "Protected minimal pair variants must not be flagged as duplicates")


class TestPipelineManifest(unittest.TestCase):

    def test_manifest_accounting(self) -> None:
        manifest = PipelineManifest(manifest_id="test_run_01", pipeline_version="1.0.0")

        r1 = PipelineRecord(
            record_id="r1",
            raw_text="ক",
            raw_sha256="hash1",
            normalized_text="ক",
            normalized_sha256="hash1",
            cleaning_metrics={"bengali_ratio": 1.0},
            dedup_decision={"tier": "UNIQUE", "is_duplicate": False},
        )
        r2 = PipelineRecord(
            record_id="r2",
            raw_text="ক",
            raw_sha256="hash1",
            normalized_text="ক",
            normalized_sha256="hash1",
            cleaning_metrics={"bengali_ratio": 1.0},
            dedup_decision={"tier": "TIER_1_EXACT", "is_duplicate": True},
        )

        manifest.add_record(r1)
        manifest.add_record(r2)

        self.assertEqual(manifest.total_input_records, 2)
        self.assertEqual(manifest.total_unique_records, 1)
        self.assertEqual(manifest.total_duplicates_removed, 1)


if __name__ == "__main__":
    unittest.main()
