"""
BLF Annotation State Machine & Promotion Governance.

Enforces strict monotonic state progression from raw ingestion to Gold:
  RAW -> CLEANED -> ANNOTATION_PENDING -> ANNOTATED_REVIEW_PENDING
      -> (IN_ADJUDICATION) -> HUMAN_PILOT_VERIFIED -> GOLD / SILVER / REJECTED / DISPUTED

Guarantees that no record can achieve GOLD status without verified human consensus.
"""

from dataclasses import dataclass, field
from enum import Enum
import re
from typing import Any, Dict, List, Optional, Set


class AnnotationRecordState(str, Enum):
    RAW = "RAW"
    CLEANED = "CLEANED"
    ANNOTATION_PENDING = "ANNOTATION_PENDING"
    ANNOTATED_REVIEW_PENDING = "ANNOTATED_REVIEW_PENDING"
    IN_ADJUDICATION = "IN_ADJUDICATION"
    HUMAN_PILOT_VERIFIED = "HUMAN_PILOT_VERIFIED"
    GOLD = "GOLD"
    SILVER = "SILVER"
    REJECTED = "REJECTED"
    DISPUTED = "DISPUTED"


@dataclass(frozen=True)
class GoldPromotionEvidence:
    """
    Explicit evidence package required before any record can achieve GOLD status.
    IAA metrics are purely descriptive/diagnostic and cannot substitute for verified consensus.
    """
    human_review_complete: bool
    review_session_id: str
    consent_record_ids: List[str]
    raw_submission_hashes: List[str]  # SHA-256 hex strings of raw immutable submissions
    decoded_record_ids: List[str]
    completeness_passed: bool
    disagreements_adjudicated_or_explicitly_resolved: bool
    evidence_review_complete: bool
    gold_gate_authorization: bool
    descriptive_iaa_score: Optional[float] = None


class IllegalPromotionError(Exception):
    """Raised when an illegal or unverified state transition is attempted."""
    pass


class PromotionStateMachine:
    """
    Validates and executes lifecycle state transitions on linguistic records.
    """

    ALLOWED_TRANSITIONS: Dict[AnnotationRecordState, Set[AnnotationRecordState]] = {
        AnnotationRecordState.RAW: {
            AnnotationRecordState.CLEANED,
            AnnotationRecordState.REJECTED,
        },
        AnnotationRecordState.CLEANED: {
            AnnotationRecordState.ANNOTATION_PENDING,
            AnnotationRecordState.REJECTED,
        },
        AnnotationRecordState.ANNOTATION_PENDING: {
            AnnotationRecordState.ANNOTATED_REVIEW_PENDING,
            AnnotationRecordState.REJECTED,
        },
        AnnotationRecordState.ANNOTATED_REVIEW_PENDING: {
            AnnotationRecordState.HUMAN_PILOT_VERIFIED,
            AnnotationRecordState.IN_ADJUDICATION,
            AnnotationRecordState.REJECTED,
        },
        AnnotationRecordState.IN_ADJUDICATION: {
            AnnotationRecordState.HUMAN_PILOT_VERIFIED,
            AnnotationRecordState.DISPUTED,
            AnnotationRecordState.REJECTED,
        },
        AnnotationRecordState.HUMAN_PILOT_VERIFIED: {
            AnnotationRecordState.GOLD,
            AnnotationRecordState.SILVER,
            AnnotationRecordState.REJECTED,
        },
        AnnotationRecordState.GOLD: set(),  # Terminal status
        AnnotationRecordState.SILVER: {AnnotationRecordState.GOLD},  # Upgradeable only with full consensus
        AnnotationRecordState.REJECTED: set(),
        AnnotationRecordState.DISPUTED: {AnnotationRecordState.IN_ADJUDICATION},
    }

    @classmethod
    def can_transition(
        cls,
        current_state: AnnotationRecordState,
        target_state: AnnotationRecordState,
    ) -> bool:
        return target_state in cls.ALLOWED_TRANSITIONS.get(current_state, set())

    @classmethod
    def transition(
        cls,
        record_id: str,
        current_state: AnnotationRecordState,
        target_state: AnnotationRecordState,
        *,
        human_verified: bool = False,
        adjudication_resolved: bool = False,
        evidence: Optional[GoldPromotionEvidence] = None,
    ) -> AnnotationRecordState:
        """
        Executes transition with invariant checks.
        """
        if not cls.can_transition(current_state, target_state):
            raise IllegalPromotionError(
                f"Cannot transition record '{record_id}' from '{current_state.value}' to '{target_state.value}'"
            )

        # Invariant 1: Promotion to HUMAN_PILOT_VERIFIED requires real human verification or adjudication
        if target_state == AnnotationRecordState.HUMAN_PILOT_VERIFIED:
            if not human_verified and not adjudication_resolved:
                raise IllegalPromotionError(
                    f"Record '{record_id}' cannot transition to HUMAN_PILOT_VERIFIED without human verification or resolved adjudication."
                )

        # Invariant 2: Promotion to GOLD requires an explicit verified GoldPromotionEvidence package
        if target_state == AnnotationRecordState.GOLD:
            if evidence is None:
                raise IllegalPromotionError(
                    f"Record '{record_id}' cannot be promoted to GOLD without an explicit GoldPromotionEvidence package."
                )
            if not evidence.human_review_complete:
                raise IllegalPromotionError(
                    f"Record '{record_id}' cannot be promoted to GOLD: human_review_complete is False."
                )
            if not evidence.review_session_id or not evidence.review_session_id.strip():
                raise IllegalPromotionError(
                    f"Record '{record_id}' cannot be promoted to GOLD: missing review_session_id."
                )
            if not evidence.consent_record_ids:
                raise IllegalPromotionError(
                    f"Record '{record_id}' cannot be promoted to GOLD: consent_record_ids is empty."
                )
            if not evidence.raw_submission_hashes:
                raise IllegalPromotionError(
                    f"Record '{record_id}' cannot be promoted to GOLD: raw_submission_hashes is empty."
                )
            for h in evidence.raw_submission_hashes:
                if not re.match(r"^[0-9a-fA-F]{64}$", h):
                    raise IllegalPromotionError(
                        f"Record '{record_id}' cannot be promoted to GOLD: invalid sha256 hex '{h}' in raw_submission_hashes."
                    )
            if record_id not in evidence.decoded_record_ids:
                raise IllegalPromotionError(
                    f"Record '{record_id}' cannot be promoted to GOLD: record_id '{record_id}' not found in decoded_record_ids."
                )
            if not evidence.completeness_passed:
                raise IllegalPromotionError(
                    f"Record '{record_id}' cannot be promoted to GOLD: completeness_passed is False."
                )
            if not evidence.disagreements_adjudicated_or_explicitly_resolved:
                raise IllegalPromotionError(
                    f"Record '{record_id}' cannot be promoted to GOLD: disagreements_adjudicated_or_explicitly_resolved is False."
                )
            if not evidence.evidence_review_complete:
                raise IllegalPromotionError(
                    f"Record '{record_id}' cannot be promoted to GOLD: evidence_review_complete is False."
                )
            if not evidence.gold_gate_authorization:
                raise IllegalPromotionError(
                    f"Record '{record_id}' cannot be promoted to GOLD: gold_gate_authorization is False."
                )

        return target_state
