"""
Unit tests for BLF Annotation State Machine, Layers, and Conflict Queues.
"""

import unittest

from blf.annotation.adjudication import AdjudicationDecision, ConflictQueue, DisagreementItem
from blf.annotation.layers import (
    DialectAnnotation,
    LayeredAnnotationBundle,
    PragmaticAnnotation,
    SemanticAnnotation,
    SyntaxAnnotation,
    TokenAnnotation,
)
from blf.annotation.state_machine import (
    AnnotationRecordState,
    IllegalPromotionError,
    PromotionStateMachine,
)


class TestAnnotationStateMachine(unittest.TestCase):

    def test_valid_progression(self) -> None:
        # RAW -> CLEANED
        s1 = PromotionStateMachine.transition("rec_1", AnnotationRecordState.RAW, AnnotationRecordState.CLEANED)
        self.assertEqual(s1, AnnotationRecordState.CLEANED)

        # CLEANED -> ANNOTATION_PENDING
        s2 = PromotionStateMachine.transition("rec_1", s1, AnnotationRecordState.ANNOTATION_PENDING)
        self.assertEqual(s2, AnnotationRecordState.ANNOTATION_PENDING)

        # ANNOTATION_PENDING -> ANNOTATED_REVIEW_PENDING
        s3 = PromotionStateMachine.transition("rec_1", s2, AnnotationRecordState.ANNOTATED_REVIEW_PENDING)
        self.assertEqual(s3, AnnotationRecordState.ANNOTATED_REVIEW_PENDING)

        # ANNOTATED_REVIEW_PENDING -> HUMAN_PILOT_VERIFIED (with human verification)
        s4 = PromotionStateMachine.transition(
            "rec_1",
            s3,
            AnnotationRecordState.HUMAN_PILOT_VERIFIED,
            human_verified=True,
        )
        self.assertEqual(s4, AnnotationRecordState.HUMAN_PILOT_VERIFIED)

        # HUMAN_PILOT_VERIFIED -> GOLD (with human verification and high IAA)
        s5 = PromotionStateMachine.transition(
            "rec_1",
            s4,
            AnnotationRecordState.GOLD,
            human_verified=True,
            iaa_score=0.88,
        )
        self.assertEqual(s5, AnnotationRecordState.GOLD)

    def test_gold_gate_invariant_rejection(self) -> None:
        # Cannot jump from RAW to GOLD
        with self.assertRaises(IllegalPromotionError):
            PromotionStateMachine.transition(
                "rec_jump",
                AnnotationRecordState.RAW,
                AnnotationRecordState.GOLD,
                human_verified=True,
                iaa_score=0.9,
            )

        # Cannot promote to GOLD without human verification
        with self.assertRaises(IllegalPromotionError):
            PromotionStateMachine.transition(
                "rec_nohuman",
                AnnotationRecordState.HUMAN_PILOT_VERIFIED,
                AnnotationRecordState.GOLD,
                human_verified=False,
                iaa_score=0.9,
            )

        # Cannot promote to GOLD with low IAA
        with self.assertRaises(IllegalPromotionError):
            PromotionStateMachine.transition(
                "rec_lowiaa",
                AnnotationRecordState.HUMAN_PILOT_VERIFIED,
                AnnotationRecordState.GOLD,
                human_verified=True,
                iaa_score=0.45,
            )


class TestAnnotationBundleAndConflictQueue(unittest.TestCase):

    def test_layered_bundle_creation(self) -> None:
        tokens = [
            TokenAnnotation(1, "সে", 0, 2, "PRON", "সে", {"Person": "3", "Polite": "Infm"}),
            TokenAnnotation(2, "বই", 3, 5, "NOUN", "বই", {"Case": "Nom"}),
            TokenAnnotation(3, "পড়ে", 6, 10, "VERB", "পড়া", {"Tense": "Pres", "Person": "3"}),
        ]
        syntax = [
            SyntaxAnnotation(1, 3, "nsubj"),
            SyntaxAnnotation(2, 3, "obj"),
            SyntaxAnnotation(3, 0, "root"),
        ]
        bundle = LayeredAnnotationBundle(
            record_id="ut_001",
            raw_text="সে বই পড়ে",
            normalized_text="সে বই পড়ে",
            tokens=tokens,
            syntax=syntax,
        )
        self.assertEqual(len(bundle.tokens), 3)
        self.assertEqual(len(bundle.syntax), 3)
        self.assertEqual(bundle.tokens[0].upos, "PRON")

    def test_conflict_queue_lifecycle(self) -> None:
        queue = ConflictQueue()
        item = DisagreementItem(
            conflict_id="cnf_01",
            record_id="ut_001",
            layer_name="syntax",
            attribute_name="deprel",
            candidate_judgments={"annotator_1": "obj", "annotator_2": "obl"},
        )
        queue.enqueue(item)
        self.assertEqual(queue.pending_count(), 1)

        decision = AdjudicationDecision(
            adjudication_id="adj_01",
            conflict_id="cnf_01",
            record_id="ut_001",
            arbitrator_id="lead_linguist",
            resolved_value="obj",
            resolution_rationale="Inanimate direct object without ke takes zero-case direct object",
        )
        resolved = queue.resolve(decision)
        self.assertIsNotNone(resolved)
        self.assertEqual(queue.pending_count(), 0)
        self.assertEqual(queue.resolved_count(), 1)


if __name__ == "__main__":
    unittest.main()
