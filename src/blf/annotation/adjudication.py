"""
BLF Conflict & Adjudication Queues.

Provides structured data containers and resolvers for inter-annotator
disagreements and arbitrator review flows.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class DisagreementItem:
    conflict_id: str
    record_id: str
    layer_name: str  # e.g. "syntax", "semantics", "tokens"
    attribute_name: str  # e.g. "deprel", "frame_id", "upos"
    candidate_judgments: Dict[str, Any]  # annotator_id -> judgment_value
    notes: Optional[str] = None
    created_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class AdjudicationDecision:
    adjudication_id: str
    conflict_id: str
    record_id: str
    arbitrator_id: str
    resolved_value: Any
    resolution_rationale: str
    resolved_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ConflictQueue:
    """Manages active inter-annotator disagreements awaiting adjudication."""

    def __init__(self) -> None:
        self.pending_disagreements: Dict[str, DisagreementItem] = {}
        self.resolved_adjudications: Dict[str, AdjudicationDecision] = {}

    def enqueue(self, item: DisagreementItem) -> None:
        self.pending_disagreements[item.conflict_id] = item

    def resolve(self, decision: AdjudicationDecision) -> Optional[DisagreementItem]:
        if decision.conflict_id not in self.pending_disagreements:
            return None
        disagreement = self.pending_disagreements.pop(decision.conflict_id)
        self.resolved_adjudications[decision.conflict_id] = decision
        return disagreement

    def pending_count(self) -> int:
        return len(self.pending_disagreements)

    def resolved_count(self) -> int:
        return len(self.resolved_adjudications)
