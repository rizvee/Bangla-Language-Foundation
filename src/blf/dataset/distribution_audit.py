"""
BLF Dataset Distribution Audit & Quota Verification.

Calculates representation distributions across registers, dialects,
semantic frames, constructions, and polarity, and audits against target quotas.
Distinguishes software test fixture quotas from production research target distributions.
"""

from collections import Counter
from dataclasses import dataclass, field
from enum import Enum
import math
from typing import Any, Dict, List, Optional, Set, Tuple


class QuotaType(str, Enum):
    SOFTWARE_TEST_QUOTA = "SOFTWARE_TEST_QUOTA"
    RESEARCH_TARGET_DISTRIBUTION = "RESEARCH_TARGET_DISTRIBUTION"


class TargetStatus(str, Enum):
    UNDEFINED = "UNDEFINED"
    PENDING_RESEARCH_DESIGN = "PENDING_RESEARCH_DESIGN"
    LOCKED_PLANNING = "LOCKED_PLANNING"


def calculate_shannon_entropy(counts: Dict[str, int], base: float = 2.0) -> float:
    """
    Calculates Shannon entropy H = -sum(p_i * log_base(p_i)) over non-empty categories.
    Descriptive diversity metric for distribution auditing.
    """
    total = sum(counts.values())
    if total <= 0:
        return 0.0
    entropy = 0.0
    for c in counts.values():
        if c > 0:
            p = c / total
            entropy -= p * (math.log(p) / math.log(base))
    return round(entropy, 4)


def calculate_simpson_diversity(counts: Dict[str, int]) -> float:
    """
    Calculates Gini-Simpson diversity index (1 - sum(p_i^2)).
    Descriptive diversity metric bounded in [0, 1).
    """
    total = sum(counts.values())
    if total <= 1:
        return 0.0
    p_sq_sum = sum((c / total) ** 2 for c in counts.values())
    return round(1.0 - p_sq_sum, 4)


@dataclass
class QuotaSpecification:
    quota_type: str = QuotaType.SOFTWARE_TEST_QUOTA.value
    target_status: str = TargetStatus.PENDING_RESEARCH_DESIGN.value
    min_registers_count: int = 4
    min_dialects_count: int = 3
    min_frames_count: int = 5
    min_constructions_count: int = 5
    required_registers: Set[str] = field(
        default_factory=lambda: {
            "formal_standard",
            "colloquial_standard",
            "intimate_conversational",
            "social_chat_shorthand",
        }
    )
    rationale: str = (
        "Default software test fixture quota thresholds. "
        "Does NOT represent an empirically justified research dataset target distribution."
    )


@dataclass
class AuditReport:
    total_records: int
    register_distribution: Dict[str, int]
    dialect_distribution: Dict[str, int]
    frame_distribution: Dict[str, int]
    construction_distribution: Dict[str, int]
    polarity_distribution: Dict[str, int]
    shannon_entropy: Dict[str, float]
    simpson_diversity: Dict[str, float]
    passed_quotas: bool
    quota_type: str = QuotaType.SOFTWARE_TEST_QUOTA.value
    target_status: str = TargetStatus.PENDING_RESEARCH_DESIGN.value
    violations: List[str] = field(default_factory=list)
    notes: str = (
        "Diversity metrics (Shannon entropy, Gini-Simpson index) are purely descriptive. "
        "They report distributional spread across software fixtures and do NOT guarantee or ensure scientific dataset balance."
    )


class DistributionAuditor:
    """
    Audits a collection of linguistic records against demographic and grammatical quotas.
    Distinguishes software test quotas from research target distributions.
    """

    def __init__(self, quota_spec: Optional[QuotaSpecification] = None) -> None:
        self.spec = quota_spec or QuotaSpecification()

    def audit(self, records: List[Dict[str, Any]]) -> AuditReport:
        reg_counts: Dict[str, int] = Counter()
        dia_counts: Dict[str, int] = Counter()
        frm_counts: Dict[str, int] = Counter()
        cst_counts: Dict[str, int] = Counter()
        pol_counts: Dict[str, int] = Counter()

        for r in records:
            if "register" in r:
                reg_counts[r["register"].lower()] += 1
            if "dialect" in r or "variety" in r:
                dia = r.get("dialect") or r.get("variety")
                dia_counts[dia.lower()] += 1
            if "semantic_frame_id" in r or "frame_id" in r:
                fid = r.get("semantic_frame_id") or r.get("frame_id")
                frm_counts[fid] += 1
            if "construction_id" in r or "primary_construction_id" in r:
                cid = r.get("construction_id") or r.get("primary_construction_id")
                cst_counts[cid] += 1
            if "polarity" in r:
                pol_counts[r["polarity"].upper()] += 1

        violations: List[str] = []

        # Check register breadth
        if len(reg_counts) < self.spec.min_registers_count:
            violations.append(
                f"Register count ({len(reg_counts)}) below fixture requirement ({self.spec.min_registers_count})"
            )

        # Check required registers
        missing_req_regs = self.spec.required_registers - set(reg_counts.keys())
        if missing_req_regs:
            violations.append(f"Missing required registers: {sorted(list(missing_req_regs))}")

        # Check dialect breadth
        if len(dia_counts) < self.spec.min_dialects_count:
            violations.append(
                f"Dialect count ({len(dia_counts)}) below fixture requirement ({self.spec.min_dialects_count})"
            )

        # Check frame breadth
        if len(frm_counts) < self.spec.min_frames_count:
            violations.append(
                f"Frame count ({len(frm_counts)}) below fixture requirement ({self.spec.min_frames_count})"
            )

        # Check construction breadth
        if len(cst_counts) < self.spec.min_constructions_count:
            violations.append(
                f"Construction count ({len(cst_counts)}) below fixture requirement ({self.spec.min_constructions_count})"
            )

        distributions = {
            "register": dict(reg_counts),
            "dialect": dict(dia_counts),
            "frame": dict(frm_counts),
            "construction": dict(cst_counts),
            "polarity": dict(pol_counts),
        }

        shannon = {k: calculate_shannon_entropy(d) for k, d in distributions.items()}
        simpson = {k: calculate_simpson_diversity(d) for k, d in distributions.items()}

        return AuditReport(
            total_records=len(records),
            register_distribution=distributions["register"],
            dialect_distribution=distributions["dialect"],
            frame_distribution=distributions["frame"],
            construction_distribution=distributions["construction"],
            polarity_distribution=distributions["polarity"],
            shannon_entropy=shannon,
            simpson_diversity=simpson,
            passed_quotas=len(violations) == 0,
            quota_type=self.spec.quota_type,
            target_status=self.spec.target_status,
            violations=violations,
        )
