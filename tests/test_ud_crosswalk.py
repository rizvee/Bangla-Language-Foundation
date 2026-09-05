"""
Unit tests for Universal Dependencies Crosswalk and Lexical Adapters.
"""

import unittest

from blf.ontology.ud_crosswalk import (
    CrosswalkRelation,
    UDCategory,
    UDCrosswalkEngine,
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

    def test_pos_mapping_vector_verb(self) -> None:
        mapping = self.engine.map_blf_to_ud("pos", "vector_verb", UDTreebank.UD_BENGALI_BRU)
        self.assertIsNotNone(mapping)
        self.assertEqual(mapping.ud_tag, "AUX")
        self.assertEqual(mapping.relation, CrosswalkRelation.CLOSE)

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

        # Mapping to frame
        aligned = adapter.map_to_frame("বই", "FRAME-COGNITIVE-ARTIFACT")
        self.assertIsNotNone(aligned)
        self.assertEqual(aligned.alignment_status, LexicalAlignmentStatus.CONFIRMED)
        self.assertEqual(aligned.metadata.get("mapped_frame_id"), "FRAME-COGNITIVE-ARTIFACT")

    def test_regional_dict_adapter(self) -> None:
        adapter = MockRegionalDictionaryAdapter()
        matches = adapter.lookup_lemma("খাইবার")
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0].dialect_flag, "regional_colloquial")


if __name__ == "__main__":
    unittest.main()
