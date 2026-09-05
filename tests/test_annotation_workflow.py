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
    GoldPromotionEvidence,
    IllegalPromotionError,
    PromotionStateMachine,
)


class TestAnnotationStateMachine(unittest.TestCase):

    def _create_valid_gold_evidence(self, record_id: str = "rec_1") -> GoldPromotionEvidence:
        return GoldPromotionEvidence(
            human_review_complete=True,
            review_session_id="SESSION_PILOT_2026_01",
            consent_record_ids=["CONSENT-REV-01", "CONSENT-REV-02"],
            raw_submission_hashes=["e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"],
            decoded_record_ids=[record_id],
            completeness_passed=True,
            disagreements_adjudicated_or_explicitly_resolved=True,
            evidence_review_complete=True,
            gold_gate_authorization=True,
            descriptive_iaa_score=0.88,
        )

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

        # HUMAN_PILOT_VERIFIED -> GOLD (with valid GoldPromotionEvidence package)
        evidence = self._create_valid_gold_evidence("rec_1")
        s5 = PromotionStateMachine.transition(
            "rec_1",
            s4,
            AnnotationRecordState.GOLD,
            evidence=evidence,
        )
        self.assertEqual(s5, AnnotationRecordState.GOLD)

    def test_gold_gate_invariant_rejection(self) -> None:
        evidence = self._create_valid_gold_evidence("rec_jump")

        # Cannot jump from RAW to GOLD
        with self.assertRaises(IllegalPromotionError):
            PromotionStateMachine.transition(
                "rec_jump",
                AnnotationRecordState.RAW,
                AnnotationRecordState.GOLD,
                evidence=evidence,
            )

        # Cannot promote to GOLD without any evidence package
        with self.assertRaises(IllegalPromotionError):
            PromotionStateMachine.transition(
                "rec_noevidence",
                AnnotationRecordState.HUMAN_PILOT_VERIFIED,
                AnnotationRecordState.GOLD,
                evidence=None,
            )

        # Cannot promote to GOLD if human_review_complete is False
        bad_evidence_1 = GoldPromotionEvidence(
            human_review_complete=False,
            review_session_id="SESSION_01",
            consent_record_ids=["C1"],
            raw_submission_hashes=["hash1"],
            decoded_record_ids=["rec_test"],
            completeness_passed=True,
            disagreements_adjudicated_or_explicitly_resolved=True,
            evidence_review_complete=True,
            gold_gate_authorization=True,
        )
        with self.assertRaises(IllegalPromotionError):
            PromotionStateMachine.transition(
                "rec_test",
                AnnotationRecordState.HUMAN_PILOT_VERIFIED,
                AnnotationRecordState.GOLD,
                evidence=bad_evidence_1,
            )

        # Cannot promote if record_id is not in decoded_record_ids
        bad_evidence_2 = GoldPromotionEvidence(
            human_review_complete=True,
            review_session_id="SESSION_01",
            consent_record_ids=["C1"],
            raw_submission_hashes=["hash1"],
            decoded_record_ids=["other_record"],
            completeness_passed=True,
            disagreements_adjudicated_or_explicitly_resolved=True,
            evidence_review_complete=True,
            gold_gate_authorization=True,
        )
        with self.assertRaises(IllegalPromotionError):
            PromotionStateMachine.transition(
                "rec_test",
                AnnotationRecordState.HUMAN_PILOT_VERIFIED,
                AnnotationRecordState.GOLD,
                evidence=bad_evidence_2,
            )

        # Cannot promote if gold_gate_authorization is False
        bad_evidence_3 = GoldPromotionEvidence(
            human_review_complete=True,
            review_session_id="SESSION_01",
            consent_record_ids=["C1"],
            raw_submission_hashes=["hash1"],
            decoded_record_ids=["rec_test"],
            completeness_passed=True,
            disagreements_adjudicated_or_explicitly_resolved=True,
            evidence_review_complete=True,
            gold_gate_authorization=False,
        )
        with self.assertRaises(IllegalPromotionError):
            PromotionStateMachine.transition(
                "rec_test",
                AnnotationRecordState.HUMAN_PILOT_VERIFIED,
                AnnotationRecordState.GOLD,
                evidence=bad_evidence_3,
            )

        # Cannot promote if disagreements are unresolved
        bad_evidence_4 = GoldPromotionEvidence(
            human_review_complete=True,
            review_session_id="SESSION_01",
            consent_record_ids=["C1"],
            raw_submission_hashes=["hash1"],
            decoded_record_ids=["rec_test"],
            completeness_passed=True,
            disagreements_adjudicated_or_explicitly_resolved=False,
            evidence_review_complete=True,
            gold_gate_authorization=True,
        )
        with self.assertRaises(IllegalPromotionError):
            PromotionStateMachine.transition(
                "rec_test",
                AnnotationRecordState.HUMAN_PILOT_VERIFIED,
                AnnotationRecordState.GOLD,
                evidence=bad_evidence_4,
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
