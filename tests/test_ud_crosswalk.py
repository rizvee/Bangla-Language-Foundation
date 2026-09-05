"""
Unit tests for Universal Dependencies Crosswalk and Lexical Adapters.
"""

import unittest

from blf.ontology.ud_crosswalk import (
    CrosswalkRelation,
    UDCategory,
    UDCrosswalkEngine,
    UDEvidenceStatus,
    UDTreebank,
)
from blf.ontology.lexical_crosswalk import (
    LexicalAlignmentStatus,
    MockAccessibleDictionaryAdapter,
    MockRegionalDictionaryAdapter,
)


class TestUDCrosswalk(unittest.TestCase):

    def setUp(self) -> None:
        self.engine = UDCrosswalkEngine()

    def test_pos_mapping_exact(self) -> None:
        mapping = self.engine.map_blf_to_ud("pos", "noun", UDTreebank.UD_BENGALI_BRU)
        self.assertIsNotNone(mapping)
        self.assertEqual(mapping.ud_tag, "NOUN")
        self.assertEqual(mapping.relation, CrosswalkRelation.EXACT)
        self.assertEqual(mapping.evidence_status, UDEvidenceStatus.OBSERVED_IN_BENGALI_BRU)

    def test_pos_mapping_vector_verb(self) -> None:
        mapping = self.engine.map_blf_to_ud("pos", "vector_verb", UDTreebank.UD_BENGALI_BRU)
        self.assertIsNotNone(mapping)
        self.assertEqual(mapping.ud_tag, "AUX")
        self.assertEqual(mapping.relation, CrosswalkRelation.CLOSE)

    def test_treebank_isolation_no_silent_fallback(self) -> None:
        # vector_verb is only mapped in UD_BENGALI_BRU, not UD_BENGALI_PUD
        mapping_pud = self.engine.map_blf_to_ud("pos", "vector_verb", UDTreebank.UD_BENGALI_PUD)
        self.assertIsNone(mapping_pud, "Must fail closed (return None) when relation is not attested in requested treebank")

        # Explicit fallback allowed
        mapping_fallback = self.engine.map_blf_to_ud("pos", "vector_verb", UDTreebank.UD_BENGALI_PUD, allow_fallback=True)
        self.assertIsNotNone(mapping_fallback)
        self.assertEqual(mapping_fallback.treebank, UDTreebank.UD_BENGALI_BRU)

    def test_feats_case_mapping(self) -> None:
        mapping = self.engine.map_blf_to_ud("case", "nominative")
        self.assertIsNotNone(mapping)
        self.assertEqual(mapping.ud_tag, "Case=Nom")
        self.assertEqual(mapping.relation, CrosswalkRelation.EXACT)

    def test_deprel_light_verb(self) -> None:
        mapping = self.engine.map_blf_to_ud("dependency", "light_verb_compound")
        self.assertIsNotNone(mapping)
        self.assertEqual(mapping.ud_tag, "compound:lvc")
        self.assertEqual(mapping.relation, CrosswalkRelation.EXACT)

    def test_unmapped_category(self) -> None:
        mapping = self.engine.map_blf_to_ud("dependency", "differential_object_flag")
        self.assertIsNotNone(mapping)
        self.assertEqual(mapping.relation, CrosswalkRelation.NO_DIRECT_MAPPING)
        self.assertEqual(mapping.evidence_status, UDEvidenceStatus.UD_SPEC_COMPATIBLE)

    def test_reverse_ud_to_blf(self) -> None:
        results = self.engine.map_ud_to_blf(UDCategory.UPOS, "VERB")
        self.assertGreater(len(results), 0)
        blf_tags = {r.blf_tag for r in results}
        self.assertIn("finite_verb", blf_tags)

    def test_relation_statistics(self) -> None:
        stats = self.engine.get_relation_statistics()
        self.assertIn("EXACT", stats)
        self.assertGreater(stats["EXACT"], 15)


class TestLexicalCrosswalk(unittest.TestCase):

    def test_accessible_dict_adapter(self) -> None:
        adapter = MockAccessibleDictionaryAdapter()
        matches = adapter.lookup_lemma("বই")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].headword, "বই")
        self.assertEqual(matches[0].alignment_status, LexicalAlignmentStatus.PROVISIONAL)
        self.assertTrue(matches[0].fixture)
        self.assertFalse(matches[0].production_eligible)
        self.assertEqual(matches[0].external_id, "MOCK-ACCESSIBLE-DICT-BOI-001")

        # Explicitly validated mapping -> CONFIRMED
        confirmed_align = adapter.map_to_frame("বই", "FRAME-00002-ARTIFACT-BOOK")
        self.assertIsNotNone(confirmed_align)
        self.assertEqual(confirmed_align.alignment_status, LexicalAlignmentStatus.CONFIRMED)

        # Unvalidated candidate frame -> PARTIAL or PROVISIONAL, never CONFIRMED
        unvalidated_align = adapter.map_to_frame("বই", "FRAME-UNVERIFIED-CONCEPT")
        self.assertIsNotNone(unvalidated_align)
        self.assertNotEqual(unvalidated_align.alignment_status, LexicalAlignmentStatus.CONFIRMED)
        self.assertIn(unvalidated_align.alignment_status, [LexicalAlignmentStatus.PROVISIONAL, LexicalAlignmentStatus.PARTIAL])

        # Unknown lemma -> UNKNOWN
        unknown_align = adapter.map_to_frame("অজানা_শব্দ", "FRAME-00001-COGNITION-READ")
        self.assertIsNotNone(unknown_align)
        self.assertEqual(unknown_align.alignment_status, LexicalAlignmentStatus.UNKNOWN)

    def test_regional_dict_adapter(self) -> None:
        adapter = MockRegionalDictionaryAdapter()
        matches = adapter.lookup_lemma("খাইবার")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].dialect_flag, "regional_colloquial")
        self.assertTrue(matches[0].fixture)
        self.assertFalse(matches[0].production_eligible)
        self.assertEqual(matches[0].external_id, "MOCK-REGDICT-KHAIBAR-001")


if __name__ == "__main__":
    unittest.main()
