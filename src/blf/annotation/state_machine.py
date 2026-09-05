"""
BLF Annotation State Machine & Promotion Governance.

Enforces strict monotonic state progression from raw ingestion to Gold:
  RAW -> CLEANED -> ANNOTATION_PENDING -> ANNOTATED_REVIEW_PENDING
      -> (IN_ADJUDICATION) -> HUMAN_PILOT_VERIFIED -> GOLD / SILVER / REJECTED / DISPUTED

Guarantees that no record can achieve GOLD status without verified human consensus.
"""

from dataclasses import dataclass, field
from enum import Enum
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
        iaa_score: Optional[float] = None,
        adjudication_resolved: bool = False,
        min_iaa_threshold: float = 0.70,
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

        # Invariant 2: Promotion to GOLD requires human verification AND IAA >= threshold
        if target_state == AnnotationRecordState.GOLD:
            if not human_verified:
                raise IllegalPromotionError(
                    f"Record '{record_id}' cannot be promoted to GOLD without verified human consensus."
                )
            if iaa_score is None or iaa_score < min_iaa_threshold:
                raise IllegalPromotionError(
                    f"Record '{record_id}' cannot be promoted to GOLD: IAA score ({iaa_score}) is below threshold ({min_iaa_threshold})."
                )

        return target_state
