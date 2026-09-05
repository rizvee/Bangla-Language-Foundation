"""
BLF Annotation OS & Quality Workflow Module.

Provides multi-layer annotation schemas, strict state machine promotion transitions,
conflict queues, and inter-annotator adjudication interfaces.
"""

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

__all__ = [
    "AdjudicationDecision",
    "AnnotationRecordState",
    "ConflictQueue",
    "DialectAnnotation",
    "DisagreementItem",
    "IllegalPromotionError",
    "LayeredAnnotationBundle",
    "PragmaticAnnotation",
    "PromotionStateMachine",
    "SemanticAnnotation",
    "SyntaxAnnotation",
    "TokenAnnotation",
]
